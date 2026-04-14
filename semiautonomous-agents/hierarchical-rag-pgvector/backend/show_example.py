"""
Real Example: Parent-Child Retrieval with Relationship Expansion

This script shows exactly how the hierarchical RAG works with actual data.
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


async def main():
    conn = await asyncpg.connect(**DB_CONFIG)

    print("=" * 80)
    print("REAL EXAMPLE: Parent-Child RAG with Relationship Expansion")
    print("=" * 80)

    # 1. Show database totals
    print("\n📊 DATABASE OVERVIEW")
    print("-" * 40)

    parent_count = await conn.fetchval("SELECT COUNT(*) FROM parent_segments")
    child_count = await conn.fetchval("SELECT COUNT(*) FROM child_chunks")
    rel_count = await conn.fetchval("SELECT COUNT(*) FROM segment_relationships")

    print(f"Total Parent Segments: {parent_count}")
    print(f"Total Child Chunks: {child_count}")
    print(f"Total Relationships: {rel_count}")

    # 2. Pick ONE specific parent from operations_manual
    print("\n" + "=" * 80)
    print("STEP 1: PICK A PARENT SEGMENT (Billing Agent from operations_manual)")
    print("=" * 80)

    parent = await conn.fetchrow("""
        SELECT parent_id, document_name, page_number, heading, agent_name, content
        FROM parent_segments
        WHERE document_name = 'operations_manual.pdf'
        AND agent_name = 'billing_agent'
        LIMIT 1
    """)

    if not parent:
        print("No billing_agent found in operations_manual.pdf")
        await conn.close()
        return

    print(f"\nParent ID: {parent['parent_id']}")
    print(f"Document: {parent['document_name']}")
    print(f"Page: {parent['page_number']}")
    print(f"Heading: {parent['heading']}")
    print(f"Agent: {parent['agent_name']}")
    print(f"\n📄 FULL PARENT CONTENT ({len(parent['content'])} chars):")
    print("-" * 40)
    print(parent['content'])
    print("-" * 40)

    # 3. Show its children WITH embeddings
    print("\n" + "=" * 80)
    print("STEP 2: CHILD CHUNKS (These are what we embed and search)")
    print("=" * 80)

    children = await conn.fetch("""
        SELECT chunk_id, content,
               CASE WHEN embedding IS NOT NULL THEN TRUE ELSE FALSE END as has_embedding
        FROM child_chunks
        WHERE parent_id = $1
        ORDER BY chunk_id
    """, parent['parent_id'])

    print(f"\nThis parent has {len(children)} child chunks:")

    for i, child in enumerate(children, 1):
        print(f"\n🔹 Child {i} (ID: {child['chunk_id'][:20]}...)")
        print(f"   Has Embedding: {'✅ YES (768-dim vector)' if child['has_embedding'] else '❌ NO'}")
        print(f"   Content ({len(child['content'])} chars):")
        print(f"   \"{child['content'][:200]}...\"" if len(child['content']) > 200 else f"   \"{child['content']}\"")

    # 4. Show relationships
    print("\n" + "=" * 80)
    print("STEP 3: AGENT RELATIONSHIPS (For expansion)")
    print("=" * 80)

    relationships = await conn.fetch("""
        SELECT target_agent, relationship_type
        FROM segment_relationships
        WHERE source_agent = $1
    """, parent['agent_name'])

    print(f"\n'{parent['agent_name']}' has {len(relationships)} relationships:")
    for rel in relationships:
        print(f"   → {rel['target_agent']} ({rel['relationship_type']})")

    # 5. Show WHY we don't get the entire document
    print("\n" + "=" * 80)
    print("STEP 4: WHY WE DON'T RETRIEVE THE ENTIRE DOCUMENT")
    print("=" * 80)

    # Count per document
    doc_stats = await conn.fetch("""
        SELECT document_name,
               COUNT(DISTINCT parent_id) as parent_count,
               (SELECT COUNT(*) FROM child_chunks cc
                WHERE cc.parent_id IN (SELECT parent_id FROM parent_segments ps2
                                       WHERE ps2.document_name = ps.document_name)) as child_count
        FROM parent_segments ps
        GROUP BY document_name
    """)

    print("\nDocument Statistics:")
    for doc in doc_stats:
        print(f"\n📁 {doc['document_name']}:")
        print(f"   Parents: {doc['parent_count']}")
        print(f"   Children: {doc['child_count']}")

    print("\n" + "-" * 40)
    print("🎯 RETRIEVAL FLOW:")
    print("-" * 40)
    print("""
1. USER QUERY: "How does billing agent handle payment failures?"

2. EMBED QUERY → 768-dimensional vector

3. VECTOR SEARCH (on child_chunks):
   - Compare query vector to ALL child embeddings
   - Return top-5 most similar children
   - Only 5 children out of {total} total!

4. PARENT LOOKUP:
   - Get parent_id from each matched child
   - Fetch full parent content (larger context)
   - Deduplicate → maybe 3 unique parents from those 5 children

5. RELATIONSHIP EXPANSION:
   - For each parent's agent_name, find relationships
   - billing_agent → [orchestrator, audit_service, ...]
   - Query: "Which segment from each related agent is most relevant?"
   - Use ANOTHER vector search to pick best segment per agent
   - Add only 1 segment per related agent (not all!)

6. FINAL CONTEXT TO LLM:
   - ~3 matched parent segments
   - ~2-3 expanded segments from related agents
   - Total: ~5-6 segments out of {total} total parents

This is ~15-20% of the document, not 100%!
""".format(total=child_count))

    # 6. Concrete numbers
    print("\n" + "=" * 80)
    print("CONCRETE EXAMPLE WITH NUMBERS")
    print("=" * 80)

    total_chars = await conn.fetchval("SELECT SUM(LENGTH(content)) FROM parent_segments")

    print(f"""
If user asks about "billing payment failures":

WHAT WE RETRIEVE:
- Top 5 children → dedupe → ~3 unique parents
- Each parent is ~500-2000 chars
- ~3 parents × ~1000 chars avg = ~3,000 chars

EXPANSION:
- billing_agent has {len(relationships)} relationships
- We pick 1 best segment per related agent
- ~{len(relationships)} segments × ~1000 chars = ~{len(relationships) * 1000} chars

TOTAL RETRIEVED: ~{3000 + len(relationships) * 1000:,} chars

TOTAL IN DATABASE: {total_chars:,} chars

PERCENTAGE RETRIEVED: ~{((3000 + len(relationships) * 1000) / total_chars * 100):.1f}%

🎯 We get FOCUSED context, not the entire document!
""")

    await conn.close()
    print("\n✅ Done!")


if __name__ == "__main__":
    asyncio.run(main())
