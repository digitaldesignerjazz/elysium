"""VectorMemory - Persistent semantic memory layer using ChromaDB.

Replaces simple in-memory list with production-grade vector storage + retrieval.
Designed for long-running agents, roleplay consistency, and self-improvement.
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
    Persistent vector memory backed by ChromaDB.
    Each agent gets its own collection for isolation.
    """

    def __init__(
        self,
        agent_id: str,
        persist_directory: str = "./memory_store",
        embedding_model_name: str = "all-MiniLM-L6-v2",
        collection_name: Optional[str] = None,
    ):
        self.agent_id = agent_id
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)

        # Initialize persistent Chroma client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )

        self.collection_name = collection_name or f"agent_{agent_id[:8]}"

        # Use local sentence-transformers embeddings (no API key required)
        self.embedding_model = SentenceTransformer(embedding_model_name)

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}  # Good for semantic similarity
        )

    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding for a piece of text."""
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
        """Add a new memory entry with embedding and rich metadata."""
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

        # Use timestamp + hash as unique ID
        doc_id = f"mem_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[meta],
        )
        return doc_id

    def search_relevant(
        self,
        query: str,
        top_k: int = 5,
        min_importance: float = 0.0,
        filter_tags: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Semantic search for relevant memories."""
        if not query.strip():
            return []

        query_embedding = self._get_embedding(query)

        # Build where filter
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
        """Return most recent memories (by timestamp in metadata)."""
        # Chroma doesn't have native sort by metadata easily, so we get all and sort
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

        # Sort by timestamp descending
        memories.sort(
            key=lambda x: x["metadata"].get("timestamp", ""), reverse=True
        )
        return memories[:limit]

    def get_stats(self) -> Dict[str, Any]:
        """Return basic statistics about the memory store."""
        count = self.collection.count()
        return {
            "agent_id": self.agent_id,
            "collection": self.collection_name,
            "total_memories": count,
            "persist_directory": self.persist_directory,
        }

    def prune_low_importance(self, threshold: float = 0.3) -> int:
        """Remove memories below importance threshold. Returns number removed."""
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
        """Dangerous: delete entire collection for this agent."""
        self.client.delete_collection(self.collection_name)
        # Recreate empty collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def __repr__(self):
        return f"<VectorMemory agent={self.agent_id[:8]} memories={self.collection.count()}>"