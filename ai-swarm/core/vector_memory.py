"""VectorMemory - Persistent semantic memory with LLM-powered consolidation.

Supports both heuristic and high-quality LLM-based memory consolidation.
"""

from __future__ import annotations
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

try:
    from .llm_client import LLMClient
except ImportError:
    LLMClient = None  # type: ignore


class VectorMemory:
    """
    Persistent vector memory + LLM-enhanced consolidation.
    """

    def __init__(
        self,
        agent_id: str,
        persist_directory: str = "./memory_store",
        embedding_model_name: str = "all-MiniLM-L6-v2",
        collection_name: Optional[str] = None,
        consolidation_threshold: int = 40,
        llm_client: Optional[Any] = None,   # LLMClient instance
        use_llm_for_consolidation: bool = False,
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
        self.llm_client = llm_client
        self.use_llm_for_consolidation = use_llm_for_consolidation and (llm_client is not None)

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

        if self.collection.count() > self.consolidation_threshold:
            self.consolidate_memories()

        return doc_id

    def search_relevant(
        self, query: str, top_k: int = 5, min_importance: float = 0.0, filter_tags: Optional[List[str]] = None
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

        memories.sort(key=lambda x: x["metadata"].get("timestamp", ""), reverse=True)
        return memories[:limit]

    def get_stats(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "collection": self.collection_name,
            "total_memories": self.collection.count(),
            "persist_directory": self.persist_directory,
            "consolidation_threshold": self.consolidation_threshold,
            "llm_consolidation_enabled": self.use_llm_for_consolidation,
        }

    # ------------------------------------------------------------------
    # MEMORY CONSOLIDATION (now with LLM support)
    # ------------------------------------------------------------------
    def consolidate_memories(
        self,
        min_memories_to_trigger: Optional[int] = None,
        max_source_memories: int = 12,
        min_importance_for_summary: float = 0.35,
    ) -> Dict[str, Any]:
        """
        Consolidate raw memories into higher-level insights.

        Uses LLM when available and enabled, otherwise falls back to heuristic.
        """
        threshold = min_memories_to_trigger or self.consolidation_threshold
        current_count = self.collection.count()

        if current_count < threshold:
            return {"status": "skipped", "reason": "below threshold", "count": current_count}

        recent_memories = self.get_recent_memories(limit=max_source_memories)

        candidates = [
            m for m in recent_memories
            if m["metadata"].get("importance", 0.5) >= min_importance_for_summary
            and "consolidated" not in m["metadata"].get("tags", [])
        ]

        if len(candidates) < 3:
            return {"status": "skipped", "reason": "not enough high-value candidates", "candidates": len(candidates)}

        memory_texts = []
        for mem in candidates:
            ts = mem["metadata"].get("timestamp", "")[:16]
            memory_texts.append(f"[{ts}] {mem['content'][:220]}")

        # Choose summarization method
        if self.use_llm_for_consolidation and self.llm_client is not None:
            summary_content = self._generate_llm_consolidation_summary(memory_texts, candidates)
            method = "llm"
        else:
            summary_content = self._generate_heuristic_consolidation_summary(memory_texts, candidates)
            method = "heuristic"

        if not summary_content:
            return {"status": "failed", "reason": "empty summary"}

        summary_id = self.add_memory(
            content=summary_content,
            tags=["consolidated", "summary", "semantic"],
            importance=0.93,
            emotional_valence=sum(m["metadata"].get("emotional_valence", 0) for m in candidates) / max(len(candidates), 1),
            source="consolidation_engine",
            metadata={
                "consolidated_from_count": len(candidates),
                "consolidation_method": method,
                "consolidation_timestamp": datetime.utcnow().isoformat(),
                "source_memory_ids": [m["id"] for m in candidates],
            },
        )

        return {
            "status": "success",
            "method": method,
            "summary_id": summary_id,
            "consolidated_memories": len(candidates),
            "new_total": self.collection.count(),
        }

    def _generate_llm_consolidation_summary(
        self, memory_texts: List[str], candidates: List[Dict]
    ) -> str:
        """High-quality abstractive summary using LLM (Grok/xAI recommended)."""
        if not self.llm_client:
            return self._generate_heuristic_consolidation_summary(memory_texts, candidates)

        prompt = (
            "You are an expert memory consolidation engine for autonomous AI agents in the Elysium ecosystem. "
            "Your job is to synthesize many individual experiences into one or two high-level, actionable insights or patterns. "
            "Focus on recurring themes, emotional tone, strategic implications, and recommendations for future behavior. "
            "Be concise but insightful. Output only the consolidated insight.

"
            "Here are the recent experiences to consolidate:\n\n" + "\n".join(memory_texts)
        )

        system_prompt = (
            "You are a precise, thoughtful memory synthesis engine. "
            "You help AI agents turn raw experience into wisdom. "
            "Always respond with clear, high-signal insights."
        )

        try:
            summary = self.llm_client.simple_completion(prompt=prompt, system_prompt=system_prompt)
            return f"**LLM-Consolidated Insight**:\n{summary}"
        except Exception as e:
            print(f"[VectorMemory] LLM consolidation failed: {e}. Falling back to heuristic.")
            return self._generate_heuristic_consolidation_summary(memory_texts, candidates)

    def _generate_heuristic_consolidation_summary(
        self, memory_texts: List[str], candidates: List[Dict]
    ) -> str:
        """Fallback heuristic/template-based summarization."""
        if not memory_texts:
            return ""

        themes = set()
        for mem in candidates:
            tags = mem["metadata"].get("tags", [])
            themes.update([t for t in tags if t not in ["action", "reflection"]])

        avg_valence = sum(m["metadata"].get("emotional_valence", 0) for m in candidates) / max(len(candidates), 1)

        summary = (
            f"**Consolidated Insight** ({len(candidates)} experiences):\n"
            f"Key themes: {', '.join(sorted(themes)) if themes else 'general activity'}.\n"
            f"Average emotional tone: {avg_valence:+.2f}.\n"
            f"Observed patterns: {memory_texts[0][:140]}...\n"
            f"Recommendation: Monitor these themes and adjust strategy or emotional responses accordingly."
        )
        return summary

    def get_consolidated_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
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
        return f"<VectorMemory agent={self.agent_id[:8]} memories={self.collection.count()} LLM={self.use_llm_for_consolidation}>"