"""Firestore data access layer with native vector search."""

import os
import logging

from google.cloud import firestore
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure

logger = logging.getLogger(__name__)

SESSIONS_COLLECTION = "sessions"
KNOWLEDGE_COLLECTION = "knowledge"
PLAYBOOKS_COLLECTION = "playbooks"


class FirestoreClient:
    """Firestore client for knowledge base operations."""

    def __init__(self, project_id: str | None = None, database_id: str = "(default)"):
        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
        self.database_id = database_id
        self._client: firestore.AsyncClient | None = None

    @property
    def client(self) -> firestore.AsyncClient:
        if self._client is None:
            self._client = firestore.AsyncClient(
                project=self.project_id,
                database=self.database_id,
            )
        return self._client

    async def session_exists(self, session_id: str) -> bool:
        """Check if a session has already been ingested."""
        doc_ref = self.client.collection(SESSIONS_COLLECTION).document(session_id)
        doc = await doc_ref.get()
        return doc.exists

    async def store_session(self, session_data: dict) -> str:
        """Store session metadata."""
        session_id = session_data["session_id"]
        doc_ref = self.client.collection(SESSIONS_COLLECTION).document(session_id)
        await doc_ref.set(session_data)
        logger.info(f"Stored session: {session_id}")
        return session_id

    async def store_knowledge_items(self, items: list[dict], deduplicate: bool = True) -> int:
        """Batch-write knowledge items to Firestore.

        Args:
            items: List of knowledge items to store.
            deduplicate: If True, skip items that already exist (based on session_id + problem hash).
        """
        batch = self.client.batch()
        count = 0
        skipped = 0

        # Build set of existing hashes for deduplication
        existing_hashes = set()
        if deduplicate:
            async for doc in self.client.collection(KNOWLEDGE_COLLECTION).stream():
                data = doc.to_dict()
                item_hash = self._item_hash(data.get("session_id", ""), data.get("problem", ""))
                existing_hashes.add(item_hash)

        for i, item in enumerate(items):
            # Check for duplicates
            if deduplicate:
                item_hash = self._item_hash(item.get("session_id", ""), item.get("problem", ""))
                if item_hash in existing_hashes:
                    skipped += 1
                    continue
                existing_hashes.add(item_hash)

            doc_ref = self.client.collection(KNOWLEDGE_COLLECTION).document()
            doc_data = {**item}
            if doc_data.get("embedding"):
                doc_data["embedding"] = Vector(doc_data["embedding"])
            batch.set(doc_ref, doc_data)
            count += 1

            if (i + 1) % 500 == 0:
                await batch.commit()
                batch = self.client.batch()
                logger.info(f"Committed batch of 500 items ({count} total)")

        if count % 500 != 0:
            await batch.commit()

        logger.info(f"Stored {count} knowledge items (skipped {skipped} duplicates)")
        return count

    def _item_hash(self, session_id: str, problem: str) -> str:
        """Generate a hash for deduplication based on session_id and problem."""
        import hashlib
        content = f"{session_id}:{problem[:200]}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    async def vector_search(
        self,
        query_embedding: list[float],
        top_k: int = 3,
        service_filter: str | None = None,
    ) -> list[dict]:
        """Semantic search using Firestore native vector search."""
        collection = self.client.collection(KNOWLEDGE_COLLECTION)

        query = collection.find_nearest(
            vector_field="embedding",
            query_vector=Vector(query_embedding),
            distance_measure=DistanceMeasure.COSINE,
            limit=top_k,
        )

        results = []
        async for doc in query.stream():
            data = doc.to_dict()
            data.pop("embedding", None)
            data["doc_id"] = doc.id
            results.append(data)

        if service_filter:
            results = [
                r for r in results
                if service_filter.lower() in [s.lower() for s in r.get("services", [])]
            ]

        return results

    async def get_knowledge_by_session(
        self,
        session_id: str,
    ) -> list[dict]:
        """Get all knowledge items for a session."""
        collection = self.client.collection(KNOWLEDGE_COLLECTION)
        query = collection.where("session_id", "==", session_id)

        results = []
        async for doc in query.stream():
            data = doc.to_dict()
            data.pop("embedding", None)
            data["doc_id"] = doc.id
            results.append(data)

        return results

    async def get_expanded_context(
        self,
        session_id: str,
        start_idx: int,
        end_idx: int,
    ) -> list[dict]:
        """Get expanded conversation messages for a specific window."""
        items = await self.get_knowledge_by_session(session_id)

        best_item = None
        best_overlap = 0
        for item in items:
            window = item.get("window", [0, 0])
            overlap = max(0, min(window[1], end_idx) - max(window[0], start_idx))
            if overlap > best_overlap:
                best_overlap = overlap
                best_item = item

        if best_item and best_item.get("expanded_messages"):
            return best_item["expanded_messages"]
        return []

    async def get_recent(
        self,
        limit: int = 10,
        service_filter: str | None = None,
        ascending: bool = False,
    ) -> list[dict]:
        """Get knowledge items ordered by timestamp."""
        collection = self.client.collection(KNOWLEDGE_COLLECTION)
        direction = firestore.Query.ASCENDING if ascending else firestore.Query.DESCENDING
        query = collection.order_by("timestamp", direction=direction).limit(limit)

        results = []
        async for doc in query.stream():
            data = doc.to_dict()
            data.pop("embedding", None)
            data["doc_id"] = doc.id
            results.append(data)

        if service_filter:
            results = [
                r for r in results
                if service_filter.lower() in [s.lower() for s in r.get("services", [])]
            ]

        return results

    async def get_topic_timeline(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        service_filter: str | None = None,
    ) -> list[dict]:
        """Get knowledge items related to a topic, sorted chronologically (oldest first).

        Uses vector search to find related items, then sorts by timestamp ascending
        to show how a topic evolved over time across multiple sessions.
        """
        collection = self.client.collection(KNOWLEDGE_COLLECTION)

        # Get more results than needed to allow for filtering
        query = collection.find_nearest(
            vector_field="embedding",
            query_vector=Vector(query_embedding),
            distance_measure=DistanceMeasure.COSINE,
            limit=top_k * 3,  # Fetch extra for filtering
        )

        results = []
        async for doc in query.stream():
            data = doc.to_dict()
            data.pop("embedding", None)
            data["doc_id"] = doc.id
            results.append(data)

        # Filter by service if specified
        if service_filter:
            results = [
                r for r in results
                if service_filter.lower() in [s.lower() for s in r.get("services", [])]
            ]

        # Sort by timestamp ascending (oldest first) to show chronological evolution
        results.sort(key=lambda x: x.get("timestamp", ""))

        # Return top_k after sorting
        return results[:top_k]

    # ---- Playbook methods ----

    async def store_playbook_items(self, items: list[dict], deduplicate: bool = True) -> int:
        """Batch-write playbook items to Firestore.

        Args:
            items: List of playbook items to store.
            deduplicate: If True, skip items that already exist (based on title hash).
        """
        batch = self.client.batch()
        count = 0
        skipped = 0

        # Build set of existing titles for deduplication
        existing_titles = set()
        if deduplicate:
            async for doc in self.client.collection(PLAYBOOKS_COLLECTION).stream():
                data = doc.to_dict()
                existing_titles.add(data.get("title", "").lower().strip())

        for i, item in enumerate(items):
            # Check for duplicates
            if deduplicate:
                title = item.get("title", "").lower().strip()
                if title in existing_titles:
                    skipped += 1
                    continue
                existing_titles.add(title)

            doc_ref = self.client.collection(PLAYBOOKS_COLLECTION).document()
            doc_data = {**item}
            if doc_data.get("embedding"):
                doc_data["embedding"] = Vector(doc_data["embedding"])
            batch.set(doc_ref, doc_data)
            count += 1

            if (i + 1) % 500 == 0:
                await batch.commit()
                batch = self.client.batch()

        if count % 500 != 0:
            await batch.commit()

        logger.info(f"Stored {count} playbook items (skipped {skipped} duplicates)")
        return count

    async def vector_search_playbooks(
        self,
        query_embedding: list[float],
        top_k: int = 3,
        project_filter: str | None = None,
        category_filter: str | None = None,
    ) -> list[dict]:
        """Semantic search over playbook entries."""
        collection = self.client.collection(PLAYBOOKS_COLLECTION)

        query = collection.find_nearest(
            vector_field="embedding",
            query_vector=Vector(query_embedding),
            distance_measure=DistanceMeasure.COSINE,
            limit=top_k,
        )

        results = []
        async for doc in query.stream():
            data = doc.to_dict()
            data.pop("embedding", None)
            data["doc_id"] = doc.id
            results.append(data)

        if project_filter:
            results = [
                r for r in results
                if project_filter.lower() in r.get("project", "").lower()
            ]
        if category_filter:
            results = [
                r for r in results
                if r.get("category", "").lower() == category_filter.lower()
            ]

        return results

    async def get_recent_playbooks(
        self,
        limit: int = 10,
        project_filter: str | None = None,
    ) -> list[dict]:
        """Get playbook items ordered by timestamp."""
        collection = self.client.collection(PLAYBOOKS_COLLECTION)
        query = collection.order_by(
            "timestamp", direction=firestore.Query.DESCENDING
        ).limit(limit)

        results = []
        async for doc in query.stream():
            data = doc.to_dict()
            data.pop("embedding", None)
            data["doc_id"] = doc.id
            results.append(data)

        if project_filter:
            results = [
                r for r in results
                if project_filter.lower() in r.get("project", "").lower()
            ]

        return results

    async def delete_by_title(self, title_query: str, collection_name: str | None = None) -> list[dict]:
        """Delete items matching a title query (case-insensitive substring).

        Searches both knowledge and playbooks collections unless specified.
        Returns list of deleted items with their collection and title/problem.
        """
        deleted = []
        title_lower = title_query.lower()

        collections = (
            [collection_name] if collection_name
            else [KNOWLEDGE_COLLECTION, PLAYBOOKS_COLLECTION]
        )

        for coll_name in collections:
            async for doc in self.client.collection(coll_name).stream():
                data = doc.to_dict()
                # Match against title (playbooks) or problem (knowledge)
                match_field = data.get("title", "") or data.get("problem", "")
                if title_lower in match_field.lower():
                    await self.client.collection(coll_name).document(doc.id).delete()
                    deleted.append({
                        "collection": coll_name,
                        "doc_id": doc.id,
                        "title": match_field[:100],
                    })
                    logger.info(f"Deleted {coll_name}/{doc.id}: {match_field[:60]}")

        return deleted

    async def get_stats(self) -> dict:
        """Get knowledge base statistics."""
        knowledge_count = 0
        playbook_count = 0
        session_count = 0
        services_counter: dict[str, int] = {}
        model_counter: dict[str, int] = {}
        category_counter: dict[str, int] = {}
        avg_score = 0.0

        async for doc in self.client.collection(KNOWLEDGE_COLLECTION).stream():
            data = doc.to_dict()
            knowledge_count += 1
            avg_score += data.get("solution_score", 0.0)
            for svc in data.get("services", []):
                services_counter[svc] = services_counter.get(svc, 0) + 1
            model = data.get("model_id", "unknown")
            model_counter[model] = model_counter.get(model, 0) + 1

        async for doc in self.client.collection(PLAYBOOKS_COLLECTION).stream():
            data = doc.to_dict()
            playbook_count += 1
            cat = data.get("category", "idea")
            category_counter[cat] = category_counter.get(cat, 0) + 1

        async for _ in self.client.collection(SESSIONS_COLLECTION).stream():
            session_count += 1

        if knowledge_count > 0:
            avg_score /= knowledge_count

        return {
            "total_knowledge_items": knowledge_count,
            "total_playbook_items": playbook_count,
            "total_sessions": session_count,
            "average_solution_score": round(avg_score, 3),
            "top_services": sorted(services_counter.items(), key=lambda x: -x[1])[:10],
            "top_models": sorted(model_counter.items(), key=lambda x: -x[1])[:5],
            "playbook_categories": sorted(category_counter.items(), key=lambda x: -x[1]),
        }
