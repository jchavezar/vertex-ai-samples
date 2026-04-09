#!/usr/bin/env python3
"""Batch ingest all Claude Code session histories with deduplication."""

import asyncio
import os
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from pipeline.run import run_extraction
from firestore_client import FirestoreClient


async def main():
    import argparse

    parser = argparse.ArgumentParser(description='Ingest all session histories')
    parser.add_argument('--dry-run', action='store_true', help='Preview without writing')
    parser.add_argument('--limit', type=int, default=0, help='Limit number of files to process')
    args = parser.parse_args()

    # Find all main session files (not subagents)
    claude_dir = Path.home() / ".claude" / "projects"
    jsonl_files = []

    for project_dir in claude_dir.iterdir():
        if not project_dir.is_dir():
            continue
        for f in project_dir.iterdir():
            if f.suffix == ".jsonl" and f.is_file():
                jsonl_files.append(f)

    # Sort by modification time (newest first)
    jsonl_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    if args.limit > 0:
        jsonl_files = jsonl_files[:args.limit]

    print(f"Found {len(jsonl_files)} session files")

    firestore_client = FirestoreClient()
    total_items = 0
    total_playbooks = 0
    skipped = 0
    processed = 0
    errors = 0

    for i, filepath in enumerate(jsonl_files, 1):
        session_id = filepath.stem
        file_size_mb = filepath.stat().st_size / (1024 * 1024)

        # Check if already ingested
        if not args.dry_run:
            try:
                if await firestore_client.session_exists(session_id):
                    print(f"[{i}/{len(jsonl_files)}] {session_id[:8]}... ({file_size_mb:.1f}MB): SKIPPED (already ingested)")
                    skipped += 1
                    continue
            except Exception as e:
                print(f"  Warning: Could not check session existence: {e}")

        print(f"[{i}/{len(jsonl_files)}] {session_id[:8]}... ({file_size_mb:.1f}MB): Processing...")

        try:
            result = await run_extraction(
                jsonl_path=str(filepath),
                dry_run=args.dry_run,
                max_concurrent=10,
            )
            items = result.get("items_extracted", 0)
            playbooks = result.get("playbooks_extracted", 0)
            total_items += items
            total_playbooks += playbooks
            processed += 1
            print(f"  -> {items} knowledge items, {playbooks} playbook items")
        except Exception as e:
            errors += 1
            print(f"  -> ERROR: {e}")

    print(f"\n{'=' * 50}")
    print(f"{'DRY RUN ' if args.dry_run else ''}COMPLETE")
    print(f"  Files processed: {processed}")
    print(f"  Files skipped:   {skipped} (already ingested)")
    print(f"  Errors:          {errors}")
    print(f"  Total knowledge items: {total_items}")
    print(f"  Total playbook items:  {total_playbooks}")


if __name__ == '__main__':
    asyncio.run(main())
