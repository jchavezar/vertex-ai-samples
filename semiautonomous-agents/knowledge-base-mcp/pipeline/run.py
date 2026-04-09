"""CLI entry point for batch extraction pipeline.

Usage:
    python -m pipeline.run /path/to/transcript.jsonl
    python -m pipeline.run --dry-run /path/to/transcript.jsonl
    python -m pipeline.run --output /tmp/extracted.json /path/to/transcript.jsonl
"""

import os
import sys
import json
import asyncio
import argparse
import logging
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from pipeline.parser import parse_jsonl_streaming
from pipeline.chunker import chunk_conversation
from pipeline.extractor import extract_batch, extract_playbooks_batch
from pipeline.models import TranscriptMessage, SessionMeta

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("pipeline")


def collect_session_meta(
    messages: list[TranscriptMessage],
    source_file: str,
) -> SessionMeta:
    """Build session metadata from parsed messages."""
    session_id = ""
    model_ids = set()
    total_input = 0
    total_output = 0
    first_ts = None

    for msg in messages:
        if not session_id and msg.session_id:
            session_id = msg.session_id
        if msg.model_id:
            model_ids.add(msg.model_id)
        if msg.usage:
            total_input += msg.usage.get("input_tokens", 0)
            total_output += msg.usage.get("output_tokens", 0)
        if not first_ts and msg.timestamp:
            first_ts = msg.timestamp

    query_count = sum(1 for m in messages if m.type == "user" and m.content_text)

    date_str = ""
    if first_ts:
        try:
            dt = datetime.fromisoformat(first_ts.replace("Z", "+00:00"))
            date_str = dt.strftime("%Y-%m-%d")
        except ValueError:
            date_str = first_ts[:10]

    return SessionMeta(
        session_id=session_id or Path(source_file).stem,
        date=date_str,
        query_count=query_count,
        model_ids=sorted(model_ids),
        source_file=source_file,
        total_input_tokens=total_input,
        total_output_tokens=total_output,
    )


async def run_extraction(
    jsonl_path: str,
    dry_run: bool = False,
    output_path: str | None = None,
    max_concurrent: int = 10,
) -> dict:
    """Run the full extraction pipeline on a JSONL file.

    Args:
        jsonl_path: Path to the JSONL transcript.
        dry_run: If True, extract but don't write to Firestore.
        output_path: If set, write extracted items to this JSON file.
        max_concurrent: Max concurrent LLM calls.

    Returns:
        Summary dict with counts and items.
    """
    logger.info(f"=== Starting extraction: {jsonl_path} ===")

    # Step 1: Parse
    logger.info("Step 1/4: Parsing JSONL...")
    messages = list(parse_jsonl_streaming(jsonl_path))
    logger.info(f"  Parsed {len(messages)} messages")

    # Build session metadata
    session_meta = collect_session_meta(messages, jsonl_path)
    logger.info(
        f"  Session: {session_meta.session_id}, "
        f"Date: {session_meta.date}, "
        f"Queries: {session_meta.query_count}, "
        f"Models: {session_meta.model_ids}"
    )

    # Step 2: Chunk
    logger.info("Step 2/4: Chunking into segments...")
    segments = chunk_conversation(messages, session_meta.session_id)
    logger.info(f"  Created {len(segments)} segments")

    # Step 3: Extract (knowledge + playbooks in parallel)
    logger.info(f"Step 3/5: Extracting knowledge + playbooks (max {max_concurrent} concurrent)...")
    items, playbook_items = await asyncio.gather(
        extract_batch(segments, max_concurrent),
        extract_playbooks_batch(segments, max_concurrent),
    )
    logger.info(f"  Extracted {len(items)} knowledge items + {len(playbook_items)} playbook items")

    # Print summary
    logger.info("\n=== Extraction Results ===")
    for i, item in enumerate(items, 1):
        logger.info(
            f"  [{i}] score={item.solution_score:.2f} | "
            f"{item.problem[:60]}..."
        )
        if item.failed_attempts:
            for fa in item.failed_attempts:
                logger.info(f"      FAILED [{fa.score:.1f}]: {fa.attempt[:60]}")

    if playbook_items:
        logger.info("\n=== Playbook Results ===")
        for i, pb in enumerate(playbook_items, 1):
            logger.info(f"  [{i}] [{pb.category}] {pb.title[:60]}")

    # Save to file if requested
    if output_path:
        output_data = {
            "session": session_meta.model_dump(),
            "items": [item.model_dump() for item in items],
            "extraction_stats": {
                "total_messages": len(messages),
                "total_segments": len(segments),
                "items_extracted": len(items),
                "segments_skipped": len(segments) - len(items),
            },
        }
        # Convert tuples to lists for JSON
        for item_data in output_data["items"]:
            item_data["window"] = list(item_data["window"])
            item_data.pop("embedding", None)

        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2, default=str)
        logger.info(f"\nSaved extraction results to: {output_path}")

    # Step 4+5: Load into Firestore (unless dry-run)
    if not dry_run:
        logger.info("Step 4/5: Loading knowledge into Firestore...")
        from firestore_client import FirestoreClient
        import embeddings as embedding_service
        from pipeline.loader import load_knowledge_items, load_playbook_items, load_session_meta

        fs_client = FirestoreClient()
        await load_session_meta(session_meta, fs_client)
        count = await load_knowledge_items(items, fs_client, embedding_service)
        logger.info(f"  Stored {count} knowledge items in Firestore")

        logger.info("Step 5/5: Loading playbooks into Firestore...")
        pb_count = await load_playbook_items(playbook_items, fs_client, embedding_service)
        logger.info(f"  Stored {pb_count} playbook items in Firestore")
    else:
        logger.info("Step 4/5: Dry run — skipping Firestore load")

    return {
        "session_id": session_meta.session_id,
        "total_messages": len(messages),
        "total_segments": len(segments),
        "items_extracted": len(items),
        "playbooks_extracted": len(playbook_items),
        "items": items,
        "playbook_items": playbook_items,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extract knowledge from Claude Code JSONL transcripts"
    )
    parser.add_argument("jsonl_path", help="Path to the JSONL transcript file")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Extract but don't write to Firestore",
    )
    parser.add_argument(
        "--output", "-o",
        help="Save extracted items to this JSON file",
    )
    parser.add_argument(
        "--max-concurrent", "-c",
        type=int,
        default=10,
        help="Max concurrent LLM calls (default: 10)",
    )

    args = parser.parse_args()

    if not os.path.exists(args.jsonl_path):
        print(f"Error: File not found: {args.jsonl_path}")
        sys.exit(1)

    result = asyncio.run(
        run_extraction(
            args.jsonl_path,
            dry_run=args.dry_run,
            output_path=args.output,
            max_concurrent=args.max_concurrent,
        )
    )

    print(f"\nDone: {result['items_extracted']} items from {result['total_segments']} segments")


if __name__ == "__main__":
    main()
