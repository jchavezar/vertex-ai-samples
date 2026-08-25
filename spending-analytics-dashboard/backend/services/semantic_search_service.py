import os
import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from google import genai

logger = logging.getLogger(__name__)

CACHE_DIR = "/Users/jesusarguelles/.gemini/jetski/brain/bcc57a77-5608-4a79-bef0-a6bce4cafa40/scratch"
EMBEDDINGS_CACHE_PATH = os.path.join(CACHE_DIR, "semantic_embeddings.npz")
DATASET_PATH = os.path.join(CACHE_DIR, "enriched_dataset.json")
RECEIPTS_CACHE_PATH = os.path.join(CACHE_DIR, "receipts_cache.json")

class SemanticSearchService:
    def __init__(self):
        self.project = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
        self.location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.model_name = "text-embedding-004"
        self.client = None
        self.emb_matrix = None # Shape: (N, 768)
        self.tx_ids = []
        self.tx_lookup = {}
        
        try:
            self.client = genai.Client(vertexai=True, project="vtxdemos", location="us-central1")
        except Exception as e:
            logger.error(f"Failed to initialize GenAI client: {e}")
            
        self._load_or_build_index()

    def _get_receipts(self) -> Dict[str, Any]:
        if os.path.exists(RECEIPTS_CACHE_PATH):
            try:
                with open(RECEIPTS_CACHE_PATH, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _get_dataset(self) -> List[Dict[str, Any]]:
        if os.path.exists(DATASET_PATH):
            try:
                with open(DATASET_PATH, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _load_or_build_index(self):
        dataset = self._get_dataset()
        self.tx_lookup = {t["id"]: t for t in dataset}

        if os.path.exists(EMBEDDINGS_CACHE_PATH):
            try:
                data = np.load(EMBEDDINGS_CACHE_PATH)
                self.emb_matrix = data["matrix"]
                self.tx_ids = list(data["tx_ids"])
                if len(self.tx_ids) == len(dataset) and self.emb_matrix.shape[0] == len(dataset):
                    logger.info(f"Loaded existing semantic embeddings index with {len(self.tx_ids)} transactions.")
                    return
            except Exception as e:
                logger.warning(f"Failed to load cached embeddings: {e}, rebuilding index...")

        self.rebuild_index()

    def rebuild_index(self):
        dataset = self._get_dataset()
        if not dataset:
            return

        receipts = self._get_receipts()
        self.tx_lookup = {t["id"]: t for t in dataset}
        
        texts = []
        tx_ids = []
        for t in dataset:
            tid = t["id"]
            clean_m = t.get("clean_merchant", "")
            raw_d = t.get("raw_description", "")
            cat = t.get("primary_category", "")
            subcat = t.get("subcategory", "")
            cluster_grp = t.get("cluster_group", cat)
            cluster_sub = t.get("cluster_subcategory", subcat)
            tags_str = ", ".join(t.get("brand_keywords", []))
            amt = t.get("amount", 0)
            member = t.get("card_member", "")
            
            rcpt_str = ""
            if tid in receipts:
                r = receipts[tid]
                items_list = r.get("items", []) or r.get("line_items", [])
                items = [f"{it.get('name', '')} {it.get('sku', '')}" for it in items_list]
                subject = r.get("gmail_subject", "")
                order_id = r.get("order_id", "")
                parts = []
                if order_id:
                    parts.append(f"Order: {order_id}")
                if subject:
                    parts.append(f"Subject: {subject}")
                if items:
                    parts.append(f"Items: {', '.join(items)}")
                if parts:
                    rcpt_str = f" | {' • '.join(parts)}"
            
            kw_part = f" | Tags: {tags_str}" if tags_str else ""
            txt = f"{clean_m} ({raw_d}) | {cat} > {cluster_grp} > {cluster_sub}{kw_part} | Amount: ${amt:.2f} | Card: {member}{rcpt_str}"
            texts.append(txt)
            tx_ids.append(tid)

        if not self.client:
            logger.error("GenAI client not initialized, cannot compute embeddings.")
            return

        logger.info(f"Computing semantic embeddings for {len(texts)} transactions with {self.model_name}...")
        from services.adk_receipt_agent import add_trace, PIPELINE_STATE

        add_trace("VECTOR_INDEX_START", f"🧠 Vector Embedding Subagent initialized with Vertex AI {self.model_name} across {len(texts)} ground-truth transactions...", "INFO", "EMBED_AGENT")
        if "AGENT_EMBED" in PIPELINE_STATE.get("active_lanes", {}):
            PIPELINE_STATE["active_lanes"]["AGENT_EMBED"] = {"status": "active", "merchant": f"Indexing {len(texts)} Items", "step": "COMPUTING_EMBEDDINGS", "amount": 0}

        batch_size = 50
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            batch_end = min(i + batch_size, len(texts))
            
            if "AGENT_EMBED" in PIPELINE_STATE.get("active_lanes", {}):
                PIPELINE_STATE["active_lanes"]["AGENT_EMBED"] = {
                    "status": "active",
                    "merchant": f"Batch {i+1}-{batch_end}/{len(texts)}",
                    "step": f"EMBEDDING_{self.model_name.upper()}",
                    "amount": 0
                }

            success = False
            for attempt in range(3):
                try:
                    res = self.client.models.embed_content(
                        model=self.model_name,
                        contents=batch
                    )
                    for emb in res.embeddings:
                        all_embeddings.append(emb.values)
                    success = True
                    add_trace("VECTOR_BATCH", f"⚡ Generated 768-dim embeddings for batch [{i+1} - {batch_end}/{len(texts)}] using Vertex AI {self.model_name}", "INFO", "EMBED_AGENT")
                    break
                except Exception as e:
                    logger.warning(f"Embedding batch [{i}:{batch_end}] attempt {attempt+1} failed: {e}. Reconnecting client...")
                    try:
                        self.client = genai.Client(vertexai=True, project="vtxdemos", location="us-central1")
                    except Exception:
                        pass
                    time.sleep(1.0 * (attempt + 1))

            if not success:
                logger.error(f"Failed embedding batch [{i}:{batch_end}] after 3 attempts.")
                add_trace("VECTOR_WARN", f"Embedding batch [{i+1}-{batch_end}] fallback to normalized zero vectors", "WARNING", "EMBED_AGENT")
                for _ in batch:
                    all_embeddings.append([0.0] * 768)

        mat = np.array(all_embeddings, dtype=np.float32)
        norms = np.linalg.norm(mat, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.emb_matrix = mat / norms
        self.tx_ids = tx_ids

        os.makedirs(os.path.dirname(EMBEDDINGS_CACHE_PATH), exist_ok=True)
        np.savez_compressed(EMBEDDINGS_CACHE_PATH, matrix=self.emb_matrix, tx_ids=np.array(tx_ids))
        logger.info(f"Successfully saved {len(tx_ids)} embeddings matrix ({self.emb_matrix.shape}) to cache.")

        add_trace("VECTOR_INDEX_COMPLETE", f"✅ Vector Space Synchronized! Index shape {self.emb_matrix.shape} saved for sub-millisecond local np.dot retrieval.", "SUCCESS", "EMBED_AGENT")
        if "AGENT_EMBED" in PIPELINE_STATE.get("active_lanes", {}):
            PIPELINE_STATE["active_lanes"]["AGENT_EMBED"] = {"status": "idle", "merchant": "Vector Index Ready", "step": "STANDBY", "amount": 0}

    def search(self, query: str, top_k: int = 40, similarity_threshold: float = 0.38) -> List[Dict[str, Any]]:
        q = str(query).strip()
        if not q:
            return []

        # 1. Keyword / Substring Matches
        keyword_scores = {}
        q_lower = q.lower()
        for tid, t in self.tx_lookup.items():
            merchant = t.get("clean_merchant", "").lower()
            desc = t.get("raw_description", "").lower()
            cat = t.get("primary_category", "").lower()
            subcat = t.get("subcategory", "").lower()
            cluster_sub = t.get("cluster_subcategory", "").lower()
            tags = [tg.lower() for tg in t.get("tags", [])]
            brand_kws = [k.lower() for k in t.get("brand_keywords", [])]

            if q_lower in merchant:
                keyword_scores[tid] = 1.0
            elif any(q_lower in k for k in brand_kws):
                keyword_scores[tid] = 0.95
            elif q_lower in desc:
                keyword_scores[tid] = 0.85
            elif q_lower in cluster_sub or q_lower in subcat:
                keyword_scores[tid] = 0.80
            elif q_lower in cat:
                keyword_scores[tid] = 0.70
            elif any(q_lower in tag for tag in tags):
                keyword_scores[tid] = 0.75

        # 2. Semantic Embedding Vector Search
        semantic_scores = {}
        if self.client and self.emb_matrix is not None and len(self.tx_ids) > 0:
            for attempt in range(2):
                try:
                    q_res = self.client.models.embed_content(
                        model=self.model_name,
                        contents=q
                    )
                    q_vec = np.array(q_res.embeddings[0].values, dtype=np.float32)
                    q_norm = np.linalg.norm(q_vec)
                    if q_norm > 0:
                        q_vec = q_vec / q_norm
                        # Fast cosine similarity matrix multiplication across all transactions
                        sims = np.dot(self.emb_matrix, q_vec)
                        for tid, sim in zip(self.tx_ids, sims):
                            if sim >= similarity_threshold:
                                semantic_scores[tid] = float(sim)
                    break
                except Exception as e:
                    logger.warning(f"Semantic search query embedding attempt {attempt+1} failed: {e}")
                    try:
                        self.client = genai.Client(vertexai=True, project="vtxdemos", location="us-central1")
                    except Exception:
                        pass

        # Combine keyword boost + semantic similarity
        combined_results = []
        all_candidate_ids = set(keyword_scores.keys()) | set(semantic_scores.keys())

        for tid in all_candidate_ids:
            kw_score = keyword_scores.get(tid, 0.0)
            sem_score = semantic_scores.get(tid, 0.0)
            final_score = max(kw_score, sem_score)
            
            if final_score >= similarity_threshold:
                t = self.tx_lookup.get(tid)
                if t:
                    combined_results.append({
                        "id": tid,
                        "clean_merchant": t.get("clean_merchant", ""),
                        "amount": t.get("amount", 0.0),
                        "score": round(final_score, 4),
                        "is_exact_match": kw_score >= 0.95,
                        "primary_category": t.get("primary_category", ""),
                        "card_member": t.get("card_member", ""),
                        "date": t.get("date", "")
                    })

        combined_results.sort(key=lambda x: x["score"], reverse=True)
        return combined_results[:top_k]
