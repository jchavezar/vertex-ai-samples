"""Ingest tool — clean, extract, and load JSONL transcripts via MCP."""

import json
import os
import tempfile
import logging

logger = logging.getLogger(__name__)


def _session_id_from_content(jsonl_content: str) -> str:
    """Extract sessionId from the first parseable JSONL line."""
    for line in jsonl_content.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            sid = msg.get("sessionId") or msg.get("session_id")
            if sid:
                return sid
        except Exception:
            continue
    return ""


def _resolve_path(path: str) -> str:
    """Resolve a gs:// path to a local file, or return local path as-is.

    Downloads GCS objects to a temp file for processing.
    """
    if path.startswith("gs://"):
        from google.cloud import storage

        # Parse gs://bucket/path/to/file
        parts = path[5:].split("/", 1)
        bucket_name = parts[0]
        blob_name = parts[1] if len(parts) > 1 else ""

        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        suffix = ".jsonl"
        tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        blob.download_to_filename(tmp.name)
        logger.info(f"Downloaded {path} to {tmp.name}")
        return tmp.name

    return path


def _session_id_from_path(jsonl_path: str) -> str:
    """Extract session ID from a JSONL file path (filename without extension)."""
    return os.path.splitext(os.path.basename(jsonl_path))[0]


def register_ingest_tools(mcp, firestore_client, embedding_service):

    @mcp.tool()
    async def ingest_session(
        jsonl_path: str = "",
        jsonl_content: str = "",
        dry_run: bool = False,
    ) -> str:
        """Ingest a Claude Code JSONL transcript into the knowledge base.

        Runs the full pipeline: parse -> chunk -> extract (Gemini on Vertex AI)
        -> embed -> store in Firestore.

        Accepts EITHER a path OR raw content. The server cannot read files on
        the calling client's filesystem — for client-local files (e.g. paths
        like /home/...), pass `jsonl_content` with the file's contents.

        Skips sessions that have already been ingested.

        Args:
            jsonl_path: Absolute path on the SERVER, or `gs://...` URI.
                Use this for paths the server can read (gs://, server-local).
            jsonl_content: Raw JSONL transcript as a string. Use this for
                CLIENT-local files. session_id is parsed from the content.
            dry_run: If True, extract and report but don't write to Firestore.
        """
        if not jsonl_path and not jsonl_content:
            return "Error: provide either `jsonl_path` or `jsonl_content`."

        # Determine session_id (for idempotency check)
        if jsonl_content:
            session_id = _session_id_from_content(jsonl_content)
            if not session_id:
                return "Error: could not parse sessionId from jsonl_content."
        else:
            session_id = _session_id_from_path(jsonl_path)

        if not dry_run:
            try:
                if await firestore_client.session_exists(session_id):
                    return (
                        f"Session `{session_id}` is already ingested. "
                        f"Skipping. Use `dry_run=True` to preview extraction without storing."
                    )
            except Exception as e:
                logger.warning(f"Could not check session existence: {e}")

        # Materialize content to a server-local file
        cleanup_path = None
        if jsonl_content:
            tmp = tempfile.NamedTemporaryFile(
                suffix=f"_{session_id}.jsonl", mode="w", delete=False
            )
            tmp.write(jsonl_content)
            tmp.close()
            local_path = tmp.name
            cleanup_path = local_path
        else:
            local_path = _resolve_path(jsonl_path)
            if local_path != jsonl_path:
                cleanup_path = local_path

        try:
            if not os.path.exists(local_path):
                return f"Error: File not found: {jsonl_path}"

            from pipeline.run import run_extraction

            result = await run_extraction(
                jsonl_path=local_path,
                dry_run=dry_run,
                max_concurrent=10,
            )

            items = result.get("items", [])
            playbook_items = result.get("playbook_items", [])
            lines = [
                f"## Ingestion {'(dry run) ' if dry_run else ''}Complete",
                f"- **Session:** {result['session_id']}",
                f"- **Messages parsed:** {result['total_messages']}",
                f"- **Segments created:** {result['total_segments']}",
                f"- **Knowledge items extracted:** {result['items_extracted']}",
                f"- **Playbook items extracted:** {result.get('playbooks_extracted', 0)}",
                "",
            ]

            if items:
                lines.append("### Extracted Knowledge Items:")
                for i, item in enumerate(items, 1):
                    lines.append(
                        f"{i}. [{item.solution_score:.2f}] **{item.problem}**"
                    )
                    lines.append(f"   Solution: {item.solution[:200]}")
                    if item.failed_attempts:
                        lines.append(f"   Failed attempts: {len(item.failed_attempts)}")
                    lines.append("")

            if playbook_items:
                lines.append("### Extracted Playbook Items:")
                for i, pb in enumerate(playbook_items, 1):
                    lines.append(f"{i}. [{pb.category.upper()}] **{pb.title}**")
                    lines.append(f"   {pb.content[:200]}")
                    if pb.tags:
                        lines.append(f"   Tags: {', '.join(pb.tags)}")
                    lines.append("")

            if dry_run:
                lines.append(
                    "_Dry run — nothing written to Firestore. "
                    "Run again without dry_run=True to persist._"
                )

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Ingestion failed: {e}", exc_info=True)
            return f"Error during ingestion: {e}"
        finally:
            # Clean up server-local temp files (GCS downloads or content writes)
            if cleanup_path and os.path.exists(cleanup_path):
                os.unlink(cleanup_path)

    @mcp.tool()
    async def ingest_all_sessions(sessions_dir: str, dry_run: bool = True) -> str:
        """Ingest all JSONL transcripts from a directory.

        Skips sessions that have already been ingested.
        Supports local directories only (not gs:// paths).

        Args:
            sessions_dir: Directory containing .jsonl transcript files.
            dry_run: If True (default), extract and report but don't write to Firestore.
        """
        if not os.path.isdir(sessions_dir):
            return f"Error: Directory not found: {sessions_dir}"

        from pipeline.run import run_extraction

        jsonl_files = sorted(
            f for f in os.listdir(sessions_dir) if f.endswith(".jsonl")
        )

        if not jsonl_files:
            return f"No .jsonl files found in {sessions_dir}"

        results = []
        total_items = 0
        skipped = 0

        for filename in jsonl_files:
            filepath = os.path.join(sessions_dir, filename)
            file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
            session_id = os.path.splitext(filename)[0]

            # Check idempotency
            if not dry_run:
                try:
                    if await firestore_client.session_exists(session_id):
                        results.append(f"- {filename} ({file_size_mb:.1f}MB): SKIPPED (already ingested)")
                        skipped += 1
                        continue
                except Exception:
                    pass

            try:
                result = await run_extraction(
                    jsonl_path=filepath,
                    dry_run=dry_run,
                    max_concurrent=10,
                )
                items_count = result["items_extracted"]
                total_items += items_count
                results.append(
                    f"- {filename} ({file_size_mb:.1f}MB): "
                    f"{result['total_segments']} segments -> "
                    f"{items_count} items"
                )
            except Exception as e:
                results.append(f"- {filename}: ERROR - {e}")

        lines = [
            f"## Batch Ingestion {'(dry run) ' if dry_run else ''}Complete",
            f"- **Files processed:** {len(jsonl_files) - skipped}",
            f"- **Files skipped:** {skipped} (already ingested)",
            f"- **Total items extracted:** {total_items}",
            "",
            "### Per-file results:",
            *results,
        ]

        if dry_run:
            lines.append(
                "\n_Dry run — nothing written to Firestore. "
                "Run again with dry_run=False to persist._"
            )

        return "\n".join(lines)
