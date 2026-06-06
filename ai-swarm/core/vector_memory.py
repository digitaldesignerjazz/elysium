"""VectorMemory - Persistent semantic memory layer using ChromaDB.

Now includes Memory Consolidation for long-term agents.
Part of Elysium AI Agent Swarm Framework.
"""

from __future__ import annotations
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


class VectorMemory:
    """
    Persistent vector memory backed by ChromaDB + Memory Consolidation.
    """

    def __init__(
        self,
        agent_id: str,
        persist_directory: str = "./memory_store",
        embedding_model_name: str = "all-MiniLM-L6-v2",
        collection_name: Optional[str] = None,
        consolidation_threshold: int = 40,
    ):
        self.agent_id = agent_id
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )

        self.collection_name = collection_name or f"agent_{agent_id[:8]}"
        self.consolidation_threshold = consolidation_threshold

        self.embedding_model = SentenceTransformer(embedding_model_name)

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def _get_embedding(self, text: str) -> List[float]:
        return self.embedding_model.encode(text, normalize_embeddings=True).tolist()

    def add_memory(
        self,
        content: str,
        tags: Optional[List[str]] = None,
        importance: float = 0.5,
        emotional_valence: float = 0.0,
        source: str = "agent",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        if not content or not content.strip():
            return ""

        tags = tags or []
        meta = metadata or {}
        meta.update({
            "timestamp": datetime.utcnow().isoformat(),
            "tags": tags,
            "importance": importance,
            "emotional_valence": emotional_valence,
            "source": source,
            "agent_id": self.agent_id,
        })

        embedding = self._get_embedding(content)
        doc_id = f"mem_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[meta],
        )

        # Auto-trigger consolidation if threshold exceeded
        if self.collection.count() > self.consolidation_threshold:
            self.consolidate_memories()

        return doc_id

    def search_relevant(
        self,
        query: str,
        top_k: int = 5,
        min_importance: float = 0.0,
        filter_tags: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        if not query.strip():
            return []

        query_embedding = self._get_embedding(query)
        where: Dict[str, Any] = {"importance": {"$gte": min_importance}}
        if filter_tags:
            where["tags"] = {"$in": filter_tags}

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where if where else None,
            include=["documents", "metadatas", "distances"],
        )

        memories = []
        if results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                memories.append({
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                })
        return memories

    def get_recent_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        all_results = self.collection.get(include=["documents", "metadatas"])
        if not all_results["ids"]:
            return []

        memories = []
        for i in range(len(all_results["ids"])):
            memories.append({
                "id": all_results["ids"][i],
                "content": all_results["documents"][i],
                "metadata": all_results["metadatas"][i],
            })

        memories.sort(
            key=lambda x: x["metadata"].get("timestamp", ""), reverse=True
        )
        return memories[:limit]

    def get_stats(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "collection": self.collection_name,
            "total_memories": self.collection.count(),
            "persist_directory": self.persist_directory,
            "consolidation_threshold": self.consolidation_threshold,
        }

    # ------------------------------------------------------------------
    # MEMORY CONSOLIDATION
    # ------------------------------------------------------------------
    def consolidate_memories(
        self,
        min_memories_to_trigger: Optional[int] = None,
        max_source_memories: int = 15,
        min_importance_for_summary: float = 0.4,
    ) -> Dict[str, Any]:
        """
        Consolidate many detailed memories into higher-level semantic summaries.

        This prevents memory bloat and enables long-term learning.
        Currently uses heuristic + template-based summarization.
        Future: Plug in LLM (Grok/xAI) for high-quality abstractive summaries.
        """
        threshold = min_memories_to_trigger or self.consolidation_threshold
        current_count = self.collection.count()

        if current_count < threshold:
            return {"status": "skipped", "reason": "below threshold", "count": current_count}

        # Get recent memories that are candidates for consolidation
        recent_memories = self.get_recent_memories(limit=max_source_memories)

        # Filter to memories worth consolidating
        candidates = [
            m for m in recent_memories
            if m["metadata"].get("importance", 0.5) >= min_importance_for_summary
            and "consolidated" not in m["metadata"].get("tags", [])
        ]

        if len(candidates) < 3:
            return {"status": "skipped", "reason": "not enough high-value candidates", "candidates": len(candidates)}

        # Build consolidation input
        memory_texts = []
        for mem in candidates:
            ts = mem["metadata"].get("timestamp", "")[:16]
            memory_texts.append(f"[{ts}] {mem['content'][:180]}")

        # === Heuristic + Template Summarization (replaceable with LLM later) ===
        summary_content = self._generate_consolidation_summary(memory_texts, candidates)

        if not summary_content:
            return {"status": "failed", "reason": "empty summary"}

        # Store the consolidated memory with high importance
        summary_id = self.add_memory(
            content=summary_content,
            tags=["consolidated", "summary", "semantic"],
            importance=0.92,
            emotional_valence=sum(m["metadata"].get("emotional_valence", 0) for m in candidates) / len(candidates),
            source="consolidation_engine",
            metadata={
                "consolidated_from_count": len(candidates),
                "consolidation_timestamp": datetime.utcnow().isoformat(),
                "source_memory_ids": [m["id"] for m in candidates],
            },
        )

        # Optional: Mark source memories as consolidated (we keep them for now for auditability)
        # In future we can prune or move them to an archive collection

        return {
            "status": "success",
            "summary_id": summary_id,
            "consolidated_memories": len(candidates),
            "new_total": self.collection.count(),
        }

    def _generate_consolidation_summary(
        self, memory_texts: List[str], candidates: List[Dict]
    ) -> str:
        """
        Generate a higher-level summary from raw memories.
        Currently template + heuristic based. Easy to upgrade to LLM call.
        """
        if not memory_texts:
            return ""

        # Simple heuristic summary
        themes = set()
        for mem in candidates:
            tags = mem["metadata"].get("tags", [])
            themes.update([t for t in tags if t not in ["action", "reflection"]])

        avg_valence = sum(m["metadata"].get("emotional_valence", 0) for m in candidates) / len(candidates)
        time_span = "recent period"

        summary = (
            f"**Consolidated Insight** ({len(candidates)} experiences over {time_span}):
"
            f"Key themes: {', '.join(sorted(themes)) if themes else 'general activity'}.
"
            f"Average emotional tone: {avg_valence:+.2f}.
"
            f"Main patterns observed: {memory_texts[0][:120]}... and related events.
"
            f"Recommendation for future behavior: Continue monitoring these themes and adjust strategy accordingly."
        )
        return summary

    def get_consolidated_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve previously created consolidated summaries."""
        results = self.collection.get(
            where={"tags": {"$in": ["consolidated"]}},
            include=["documents", "metadatas"],
            limit=limit,
        )

        memories = []
        if results["ids"]:
            for i in range(len(results["ids"])):
                memories.append({
                    "id": results["ids"][i],
                    "content": results["documents"][i],
                    "metadata": results["metadatas"][i],
                })
        return memories

    def prune_low_importance(self, threshold: float = 0.3) -> int:
        results = self.collection.get(include=["metadatas"])
        if not results["ids"]:
            return 0

        ids_to_delete = []
        for i, meta in enumerate(results["metadatas"]):
            if meta.get("importance", 0.5) < threshold:
                ids_to_delete.append(results["ids"][i])

        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)
        return len(ids_to_delete)

    def clear_all(self) -> None:
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def __repr__(self):
        return f"<VectorMemory agent={self.agent_id[:8]} memories={self.collection.count()}>"