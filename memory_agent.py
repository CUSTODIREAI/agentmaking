#!/usr/bin/env python3
"""
AI Agent with Local Memory and Semantic Search

Features:
- Store memories locally (SQLite + JSON)
- Semantic search using sentence embeddings
- Remember user preferences, facts, schedules
- Recall relevant memories based on context
"""

import os
import json
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

# Optional: for semantic search (install: pip install sentence-transformers numpy)
try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    SEMANTIC_ENABLED = True
except ImportError:
    SEMANTIC_ENABLED = False
    print("Note: Install sentence-transformers for semantic search: pip install sentence-transformers numpy")


class MemoryStore:
    """Local memory storage with SQLite and optional semantic search."""

    def __init__(self, storage_dir: str = None):
        self.storage_dir = Path(storage_dir or os.path.expanduser("~/agent/memories"))
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = self.storage_dir / "memory.db"
        self.embeddings_path = self.storage_dir / "embeddings.json"

        self._init_db()
        self._load_embeddings()

        # Initialize embedding model if available (force CPU to avoid VRAM conflicts)
        if SEMANTIC_ENABLED:
            self.model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        else:
            self.model = None

    def _init_db(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON memories(category)")

        # Full-text search table
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts
            USING fts5(id, content, category)
        """)
        conn.commit()
        conn.close()

    def _load_embeddings(self):
        """Load embeddings cache from disk."""
        if self.embeddings_path.exists():
            with open(self.embeddings_path, 'r') as f:
                self.embeddings_cache = json.load(f)
        else:
            self.embeddings_cache = {}

    def _save_embeddings(self):
        """Save embeddings cache to disk."""
        with open(self.embeddings_path, 'w') as f:
            json.dump(self.embeddings_cache, f)

    def _generate_id(self, content: str) -> str:
        """Generate unique ID for memory."""
        return hashlib.md5(f"{content}{datetime.now().isoformat()}".encode()).hexdigest()[:12]

    def store(self, content: str, category: str = "general", metadata: Dict = None) -> str:
        """
        Store a new memory.

        Args:
            content: The memory content
            category: Category (preferences, facts, schedule, context, history)
            metadata: Optional metadata dict

        Returns:
            Memory ID
        """
        memory_id = self._generate_id(content)
        now = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)

        # Insert into main table
        conn.execute("""
            INSERT OR REPLACE INTO memories (id, category, content, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (memory_id, category, content, json.dumps(metadata or {}), now, now))

        # Insert into FTS table
        conn.execute("""
            INSERT OR REPLACE INTO memories_fts (id, content, category)
            VALUES (?, ?, ?)
        """, (memory_id, content, category))

        conn.commit()
        conn.close()

        # Generate and cache embedding if semantic search enabled
        if self.model:
            embedding = self.model.encode(content).tolist()
            self.embeddings_cache[memory_id] = {
                "embedding": embedding,
                "content": content,
                "category": category
            }
            self._save_embeddings()

        print(f"Stored memory [{category}]: {content[:50]}...")
        return memory_id

    def search_keyword(self, query: str, limit: int = 5) -> List[Dict]:
        """Search memories using full-text search."""
        # Clean query for FTS5 - remove special characters
        clean_query = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in query)
        clean_query = ' '.join(clean_query.split())  # Normalize whitespace

        if not clean_query:
            return []

        conn = sqlite3.connect(self.db_path)
        try:
            # Use quotes for phrase matching
            cursor = conn.execute("""
                SELECT m.id, m.category, m.content, m.metadata, m.created_at
                FROM memories_fts fts
                JOIN memories m ON fts.id = m.id
                WHERE memories_fts MATCH ?
                LIMIT ?
            """, (f'"{clean_query}"', limit))
        except sqlite3.OperationalError:
            # Fallback to LIKE search
            cursor = conn.execute("""
                SELECT id, category, content, metadata, created_at
                FROM memories
                WHERE content LIKE ?
                LIMIT ?
            """, (f'%{clean_query}%', limit))

        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "category": row[1],
                "content": row[2],
                "metadata": json.loads(row[3]),
                "created_at": row[4],
                "search_type": "keyword"
            })

        conn.close()
        return results

    def search_semantic(self, query: str, limit: int = 5, threshold: float = 0.3) -> List[Dict]:
        """Search memories using semantic similarity."""
        if not self.model or not self.embeddings_cache:
            return []

        query_embedding = self.model.encode(query)

        results = []
        for memory_id, data in self.embeddings_cache.items():
            embedding = np.array(data["embedding"])

            # Cosine similarity
            similarity = np.dot(query_embedding, embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
            )

            if similarity >= threshold:
                results.append({
                    "id": memory_id,
                    "content": data["content"],
                    "category": data["category"],
                    "similarity": float(similarity),
                    "search_type": "semantic"
                })

        # Sort by similarity
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:limit]

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search memories using both keyword and semantic search.
        Combines results and removes duplicates.
        """
        results = []
        seen_ids = set()

        # Semantic search first (if available)
        if self.model:
            for r in self.search_semantic(query, limit):
                if r["id"] not in seen_ids:
                    results.append(r)
                    seen_ids.add(r["id"])

        # Keyword search
        for r in self.search_keyword(query, limit):
            if r["id"] not in seen_ids:
                results.append(r)
                seen_ids.add(r["id"])

        return results[:limit]

    def get_by_category(self, category: str) -> List[Dict]:
        """Get all memories in a category."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT id, content, metadata, created_at
            FROM memories WHERE category = ?
            ORDER BY created_at DESC
        """, (category,))

        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "content": row[1],
                "metadata": json.loads(row[2]),
                "created_at": row[3],
                "category": category
            })

        conn.close()
        return results

    def get_all(self) -> List[Dict]:
        """Get all memories."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT id, category, content, metadata, created_at
            FROM memories ORDER BY created_at DESC
        """)

        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "category": row[1],
                "content": row[2],
                "metadata": json.loads(row[3]),
                "created_at": row[4]
            })

        conn.close()
        return results

    def delete(self, memory_id: str) -> bool:
        """Delete a memory by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        conn.execute("DELETE FROM memories_fts WHERE id = ?", (memory_id,))
        conn.commit()
        conn.close()

        if memory_id in self.embeddings_cache:
            del self.embeddings_cache[memory_id]
            self._save_embeddings()

        return True

    def clear_all(self):
        """Clear all memories."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM memories")
        conn.execute("DELETE FROM memories_fts")
        conn.commit()
        conn.close()

        self.embeddings_cache = {}
        self._save_embeddings()
        print("All memories cleared.")


class MemoryAgent:
    """AI Agent with memory capabilities."""

    def __init__(self, storage_dir: str = None):
        self.memory = MemoryStore(storage_dir)
        self.categories = ["preferences", "facts", "schedule", "context", "history"]

    def remember(self, content: str, category: str = "general", metadata: Dict = None) -> str:
        """Store a new memory."""
        if category not in self.categories:
            self.categories.append(category)
        return self.memory.store(content, category, metadata)

    def recall(self, query: str, limit: int = 5) -> List[Dict]:
        """Recall memories relevant to query."""
        return self.memory.search(query, limit)

    def get_preferences(self) -> List[Dict]:
        """Get all user preferences."""
        return self.memory.get_by_category("preferences")

    def get_schedule(self) -> List[Dict]:
        """Get schedule-related memories."""
        return self.memory.get_by_category("schedule")

    def get_facts(self) -> List[Dict]:
        """Get stored facts about user."""
        return self.memory.get_by_category("facts")

    def get_context(self) -> str:
        """Get context string for prompts."""
        memories = self.memory.get_all()[:20]  # Last 20 memories
        if not memories:
            return "No memories stored yet."

        context_parts = []
        for m in memories:
            context_parts.append(f"[{m['category']}] {m['content']}")

        return "\n".join(context_parts)

    def forget(self, memory_id: str):
        """Delete a specific memory."""
        return self.memory.delete(memory_id)

    def reset(self):
        """Clear all memories."""
        self.memory.clear_all()


def interactive_demo():
    """Interactive demo of the memory agent."""
    print("\n" + "="*60)
    print("AI Memory Agent - Interactive Demo")
    print("="*60)

    agent = MemoryAgent()

    # Store some example memories
    print("\n--- Storing example memories ---")
    agent.remember("User prefers dark mode for all applications", "preferences")
    agent.remember("User's name is Alex", "facts")
    agent.remember("User works with video processing pipelines", "facts")
    agent.remember("User has RTX 4090 GPU with 24GB VRAM", "facts")
    agent.remember("Weekly team meeting on Fridays at 2pm EST", "schedule")
    agent.remember("User prefers concise, technical responses", "preferences")
    agent.remember("User timezone is EST (Eastern Standard Time)", "facts")
    agent.remember("User is working on a 1000 video batch processing job", "context")

    print("\n--- All stored memories ---")
    for m in agent.memory.get_all():
        print(f"  [{m['category']}] {m['content']}")

    print("\n--- Semantic Search: 'GPU' ---")
    results = agent.recall("GPU and video card")
    for r in results:
        score = r.get('similarity', 'N/A')
        print(f"  [{r['category']}] {r['content']} (score: {score})")

    print("\n--- Semantic Search: 'meeting schedule' ---")
    results = agent.recall("When is the meeting?")
    for r in results:
        score = r.get('similarity', 'N/A')
        print(f"  [{r['category']}] {r['content']} (score: {score})")

    print("\n--- Preferences ---")
    for p in agent.get_preferences():
        print(f"  - {p['content']}")

    print("\n--- Context for LLM prompt ---")
    print(agent.get_context())

    print("\n" + "="*60)
    print(f"Memory database: {agent.memory.db_path}")
    print(f"Embeddings cache: {agent.memory.embeddings_path}")
    print("="*60)


if __name__ == "__main__":
    interactive_demo()
