#!/usr/bin/env python3
"""Ingest playbook JSON files into Firestore with embeddings."""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from embeddings import embed_texts
from firestore_client import FirestoreClient


async def ingest_playbooks(playbook_file: str, dry_run: bool = False):
    """Ingest playbook entries from a JSON file."""

    print(f"Loading playbooks from: {playbook_file}")
    with open(playbook_file) as f:
        playbooks = json.load(f)

    print(f"Found {len(playbooks)} playbook entries")

    # Initialize services
    firestore_client = FirestoreClient()

    items_to_store = []

    for i, playbook in enumerate(playbooks):
        print(f"\n[{i+1}/{len(playbooks)}] {playbook['title']}")

        # Generate embedding from search_text
        search_text = playbook.get('search_text', playbook['title'])
        print(f"  Embedding: {search_text[:60]}...")

        embeddings = await embed_texts([search_text], task_type="RETRIEVAL_DOCUMENT")
        embedding = embeddings[0]

        item = {
            'title': playbook['title'],
            'category': playbook.get('category', 'idea'),
            'project': playbook.get('project', ''),
            'content': playbook['content'],
            'tags': playbook.get('tags', []),
            'rejected': playbook.get('rejected', []),
            'search_text': search_text,
            'embedding': embedding,
            'timestamp': datetime.utcnow().isoformat(),
            'source': playbook_file,
        }

        items_to_store.append(item)
        print(f"  Category: {item['category']}, Tags: {', '.join(item['tags'][:3])}...")

    if dry_run:
        print(f"\n[DRY RUN] Would store {len(items_to_store)} playbook items")
        for item in items_to_store:
            print(f"  - [{item['category']}] {item['title']}")
        return

    # Store in Firestore
    print(f"\nStoring {len(items_to_store)} items in Firestore...")
    count = await firestore_client.store_playbook_items(items_to_store)
    print(f"Successfully stored {count} playbook items!")


async def main():
    import argparse

    parser = argparse.ArgumentParser(description='Ingest playbooks into Firestore')
    parser.add_argument('file', help='JSON file with playbook entries')
    parser.add_argument('--dry-run', action='store_true', help='Preview without writing')

    args = parser.parse_args()

    await ingest_playbooks(args.file, dry_run=args.dry_run)


if __name__ == '__main__':
    asyncio.run(main())
