"""SwarmMemory - Shared persistent memory layer for the entire agent swarm.

Enables collective knowledge, shared consolidated insights, and swarm-level learning.
Part of the Elysium AI Agent Swarm Framework.
"""

from __future__ import annotations
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


class SwarmMemory:
    """
    Shared vector memory for a swarm of agents.

    All agents in the same swarm can read from and contribute to this collective memory.
    This enables emergent swarm intelligence and knowledge sharing.
    """

    def __init__(
        self,
        swarm_name: str,
        persist_directory: str = "./swarm_memory_store",
        embedding_model_name: str = "all-MiniLM-L6-v2",
    ):
        self.swarm_name = swarm_name
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )

        self.collection_name = f"swarm_{swarm_name.lower().replace(' ', '_')}"

        self.embedding_model = SentenceTransformer(embedding_model_name)

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine", "type": "swarm_memory"},
        )

    def _get_embedding(self, text: str) -> List[float]:
        return self.embedding_model.encode(text, normalize_embeddings=True).tolist()

    def add_shared_insight(
        self,
        content: str,
        source_agent_id: str,
        source_agent_role: str,
        importance: float = 0.8,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Add a consolidated insight from an agent to the shared swarm memory."""
        if not content or not content.strip():
            return ""

        tags = tags or []
        tags.extend(["swarm_shared", source_agent_role])

        meta = metadata or {}
        meta.update({
            "timestamp": datetime.utcnow().isoformat(),
            "source_agent_id": source_agent_id,
            "source_agent_role": source_agent_role,
            "importance": importance,
            "tags": tags,
        })

        embedding = self._get_embedding(content)
        doc_id = f"swarm_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[meta],
        )
        return doc_id

    def query_swarm_knowledge(
        self,
        query: str,
        top_k: int = 6,
        min_importance: float = 0.5,
        filter_by_role: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Semantic search across the swarm's shared knowledge."""
        if not query.strip():
            return []

        query_embedding = self._get_embedding(query)

        where: Dict[str, Any] = {"importance": {"$gte": min_importance}}
        if filter_by_role:
            where["source_agent_role"] = filter_by_role

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where if where else None,
            include=["documents", "metadatas", "distances"],
        )

        insights = []
        if results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                insights.append({
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                })
        return insights

    def get_recent_swarm_insights(self, limit: int = 8) -> List[Dict[str, Any]]:
        all_results = self.collection.get(include=["documents", "metadatas"])
        if not all_results["ids"]:
            return []

        insights = []
        for i in range(len(all_results["ids"])):
            insights.append({
                "id": all_results["ids"][i],
                "content": all_results["documents"][i],
                "metadata": all_results["metadatas"][i],
            })

        insights.sort(key=lambda x: x["metadata"].get("timestamp", ""), reverse=True)
        return insights[:limit]

    def get_stats(self) -> Dict[str, Any]:
        return {
            "swarm_name": self.swarm_name,
            "collection": self.collection_name,
            "total_shared_insights": self.collection.count(),
            "persist_directory": self.persist_directory,
        }

    def consolidate_swarm_knowledge(self, top_k: int = 10) -> Dict[str, Any]:
        """Create a higher-level swarm-level consolidated insight from recent shared knowledge."""
        recent = self.get_recent_swarm_insights(limit=top_k)
        if len(recent) < 3:
            return {"status": "skipped", "reason": "not enough insights"}

        # Simple heuristic summary for now (can be upgraded to LLM)
        themes = set()
        for item in recent:
            tags = item["metadata"].get("tags", [])
            themes.update([t for t in tags if t not in ["swarm_shared"]])

        summary = (
            f"**Swarm-Level Consolidated Insight** ({len(recent)} contributions):\n"
            f"Key themes across agents: {', '.join(sorted(themes)) if themes else 'general swarm activity'}.\n"
            f"This represents collective learning from multiple specialized agents."
        )

        self.add_shared_insight(
            content=summary,
            source_agent_id="swarm_orchestrator",
            source_agent_role="SwarmOrchestrator",
            importance=0.95,
            tags=["swarm_consolidated", "meta"],
        )

        return {
            "status": "success",
            "new_insight": summary,
            "based_on": len(recent),
        }

    def clear_all(self) -> None:
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine", "type": "swarm_memory"},
        )