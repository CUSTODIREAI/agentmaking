# AI Agent Memory Systems

How to create an AI Agent that can store 'memories' and recall relevant memories when required using semantic search.

## Overview

Agent memory enables:
- Remembering user preferences
- Storing personal details
- Managing schedules
- Providing personalized user experiences
- Learning from past interactions

## Types of Memory

### 1. Semantic Memory
Stores structured factual knowledge (facts, definitions, rules).
- Implemented via knowledge bases or vector embeddings
- Used for reasoning and retrieval

### 2. Episodic Memory
Stores specific events and experiences.
- Past conversations with users
- Previous decisions and outcomes
- User preferences expressed over time

### 3. Procedural Memory
Stores rules and procedures.
- How to perform specific tasks
- Learned behaviors and patterns

## Implementation Approaches

### Option 1: File-Based (Claude Memory Tool)

Simple, transparent approach using Markdown files:

```
/memories/
├── user_preferences.md
├── project_context.md
├── learned_facts.md
└── schedules.md
```

**Operations**: view, create, str_replace, insert, delete, rename

**Advantages**:
- No vector database needed
- Human-readable storage
- Full control over data
- Easy debugging

**Example Memory File** (`user_preferences.md`):
```markdown
# User Preferences

## Communication Style
- Prefers concise responses
- Likes code examples
- Wants technical depth

## Schedule
- Available 9am-5pm EST
- Prefers async communication
- Weekly sync on Fridays

## Projects
- Working on video pipeline
- Uses Docker + CUDA
- RTX 4090 GPU
```

### Option 2: Vector Database (Semantic Search)

For large-scale memory with similarity search:

```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import VectorStoreRetrieverMemory

# Initialize vector store
embeddings = OpenAIEmbeddings()
vectorstore = Chroma(
    collection_name="agent_memory",
    embedding_function=embeddings,
    persist_directory="./memory_db"
)

# Create retriever memory
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
memory = VectorStoreRetrieverMemory(retriever=retriever)

# Store a memory
memory.save_context(
    {"input": "My favorite color is blue"},
    {"output": "I'll remember that your favorite color is blue."}
)

# Retrieve relevant memories
relevant = memory.load_memory_variables({"prompt": "What colors do I like?"})
```

### Option 3: SQLite Local Storage (MCP Memory Server)

Portable, local-first approach:

```python
import sqlite3
import json
from datetime import datetime

class LocalMemory:
    def __init__(self, db_path="./agent/memory.db"):
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY,
                category TEXT,
                content TEXT,
                metadata TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        self.conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts
            USING fts5(content, category)
        """)
        self.conn.commit()

    def store(self, category: str, content: str, metadata: dict = None):
        now = datetime.now()
        self.conn.execute(
            "INSERT INTO memories (category, content, metadata, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (category, content, json.dumps(metadata or {}), now, now)
        )
        self.conn.execute(
            "INSERT INTO memories_fts (content, category) VALUES (?, ?)",
            (content, category)
        )
        self.conn.commit()

    def search(self, query: str, limit: int = 5):
        cursor = self.conn.execute(
            "SELECT content, category FROM memories_fts WHERE memories_fts MATCH ? LIMIT ?",
            (query, limit)
        )
        return cursor.fetchall()

    def get_by_category(self, category: str):
        cursor = self.conn.execute(
            "SELECT content, metadata FROM memories WHERE category = ?",
            (category,)
        )
        return cursor.fetchall()

# Usage
memory = LocalMemory()
memory.store("preferences", "User prefers dark mode", {"priority": "high"})
memory.store("schedule", "Weekly meeting on Fridays at 2pm")
memory.store("facts", "User works with RTX 4090 GPU")

# Search memories
results = memory.search("GPU")
```

## Semantic Search with Embeddings

For similarity-based memory retrieval:

```python
import numpy as np
from sentence_transformers import SentenceTransformer

class SemanticMemory:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.memories = []
        self.embeddings = []

    def store(self, text: str, metadata: dict = None):
        embedding = self.model.encode(text)
        self.memories.append({"text": text, "metadata": metadata or {}})
        self.embeddings.append(embedding)

    def search(self, query: str, top_k: int = 5):
        query_embedding = self.model.encode(query)

        # Cosine similarity
        similarities = []
        for emb in self.embeddings:
            sim = np.dot(query_embedding, emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(emb)
            )
            similarities.append(sim)

        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        return [
            {"memory": self.memories[i], "score": similarities[i]}
            for i in top_indices
        ]

# Usage
memory = SemanticMemory()
memory.store("User prefers morning meetings")
memory.store("User's timezone is EST")
memory.store("User likes Python over JavaScript")
memory.store("User works on video processing pipelines")

# Semantic search - finds related memories
results = memory.search("When should I schedule calls?")
# Returns: morning meetings, timezone info
```

## Memory Categories

Organize memories by type:

| Category | Examples | Retrieval |
|----------|----------|-----------|
| `preferences` | UI theme, communication style | Exact match |
| `facts` | Name, location, tools used | Keyword search |
| `schedule` | Meetings, availability | Date filtering |
| `context` | Current projects, goals | Semantic search |
| `history` | Past interactions | Time-based |

## Best Practices

1. **Scope memories to projects** - Don't mix contexts
2. **Set retention policies** - Auto-expire old memories
3. **User controls** - Allow pause/reset/export
4. **Privacy first** - Store locally when possible
5. **Chunking** - Break large memories into discrete units
6. **Metadata** - Add timestamps, sources, confidence scores

## Local Storage Structure

```
/home/user/agent/
├── memory.db              # SQLite database
├── memories/              # Markdown files
│   ├── preferences.md
│   ├── context.md
│   └── schedule.md
├── embeddings/            # Vector cache
│   └── memories.npy
└── config.json            # Memory settings
```

## References

- [LangGraph Memory Semantic Search](https://langchain-ai.github.io/langgraph/how-tos/memory/semantic-search/)
- [Claude Memory Tool Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool)
- [MongoDB LangGraph Memory](https://www.mongodb.com/company/blog/product-release-announcements/powering-long-term-memory-for-agents-langgraph)
- [Redis AI Agent Memory](https://redis.io/blog/build-smarter-ai-agents-manage-short-term-and-long-term-memory-with-redis/)
- [IBM AI Agent Memory](https://www.ibm.com/think/topics/ai-agent-memory)
