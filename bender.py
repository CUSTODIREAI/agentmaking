#!/usr/bin/env python3
"""
Bender - AI Memory Agent
Ask: bender "how many containers safe?"
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory_agent import MemoryAgent

def bender_ask(query: str):
    """Ask Bender a question."""
    agent = MemoryAgent(os.path.expanduser("~/agent/memories"))
    results = agent.recall(query, limit=5)

    if not results:
        print("Bender: I don't know that yet. Teach me with: bender learn \"fact\" category")
        return

    print("Bender:")
    for r in results:
        score = r.get('similarity', '')
        score_str = f" ({score:.0%})" if score else ""
        print(f"  → {r['content']}{score_str}")

def bender_learn(content: str, category: str = "learned"):
    """Teach Bender something new."""
    agent = MemoryAgent(os.path.expanduser("~/agent/memories"))
    agent.remember(content, category)
    print(f"Bender: Got it! Stored in [{category}]")

def bender_list(category: str = None):
    """List memories."""
    agent = MemoryAgent(os.path.expanduser("~/agent/memories"))
    memories = agent.memory.get_all()

    if category:
        memories = [m for m in memories if m['category'] == category]

    print(f"Bender's memories ({len(memories)}):")
    for m in memories:
        print(f"  [{m['category']}] {m['content'][:80]}")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  bender \"question\"           - Ask Bender")
        print("  bender learn \"fact\" [cat]   - Teach Bender")
        print("  bender list [category]       - List memories")
        print("  bender forget                - Clear all memories")
        return

    cmd = sys.argv[1]

    if cmd == "learn" and len(sys.argv) >= 3:
        content = sys.argv[2]
        category = sys.argv[3] if len(sys.argv) > 3 else "learned"
        bender_learn(content, category)
    elif cmd == "list":
        category = sys.argv[2] if len(sys.argv) > 2 else None
        bender_list(category)
    elif cmd == "forget":
        agent = MemoryAgent(os.path.expanduser("~/agent/memories"))
        agent.reset()
        print("Bender: Memory wiped!")
    else:
        # It's a question
        query = " ".join(sys.argv[1:])
        bender_ask(query)

if __name__ == "__main__":
    main()
