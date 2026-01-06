#!/usr/bin/env python3
"""
SuperBender - AI Memory Agent + Changelog Tracker
Central brain for knowledge, insights, and pipeline evolution.

Usage:
  bender "question"              - Semantic search
  bender learn "fact" [category] - Store knowledge
  bender log "change details"    - Log timestamped changelog entry
  bender changelog [n]           - Show last n changes (default 10)
  bender today                   - Show today's entries
  bender week                    - Show this week's entries
  bender stats                   - Show memory statistics
  bender list [category]         - List all memories
  bender categories              - List all categories
  bender export                  - Export all memories to JSON
  bender forget                  - Clear all memories
"""

import sys
import os
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from memory_agent import MemoryAgent

MEMORY_PATH = os.path.expanduser("~/agent/memories")

def get_agent():
    return MemoryAgent(MEMORY_PATH)

def bender_ask(query: str):
    """Ask Bender a question (semantic search)."""
    agent = get_agent()
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
    agent = get_agent()
    agent.remember(content, category)
    print(f"Bender: Got it! Stored in [{category}]")

def bender_log(content: str):
    """Log a timestamped changelog entry."""
    agent = get_agent()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"[{timestamp}] {content}"
    agent.remember(entry, "changelog")
    print(f"Bender: Logged to changelog")

def bender_changelog(limit: int = 10):
    """Show recent changelog entries."""
    agent = get_agent()
    memories = agent.memory.get_by_category("changelog")

    print(f"Bender Changelog (last {min(limit, len(memories))}):")
    print("-" * 60)
    for m in memories[:limit]:
        print(f"{m['content']}")
        print()

def bender_today():
    """Show today's entries."""
    agent = get_agent()
    memories = agent.memory.get_all()
    today = datetime.now().date().isoformat()

    today_memories = [m for m in memories if m['created_at'].startswith(today)]

    print(f"Bender - Today ({today}) - {len(today_memories)} entries:")
    print("-" * 60)
    for m in today_memories:
        time = m['created_at'][11:16]
        print(f"  [{time}] [{m['category']}] {m['content'][:70]}")

def bender_week():
    """Show this week's entries."""
    agent = get_agent()
    memories = agent.memory.get_all()
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()

    week_memories = [m for m in memories if m['created_at'] >= week_ago]

    print(f"Bender - This Week - {len(week_memories)} entries:")
    print("-" * 60)

    # Group by date
    by_date = {}
    for m in week_memories:
        date = m['created_at'][:10]
        if date not in by_date:
            by_date[date] = []
        by_date[date].append(m)

    for date in sorted(by_date.keys(), reverse=True):
        print(f"\n{date}:")
        for m in by_date[date]:
            print(f"  [{m['category']}] {m['content'][:60]}")

def bender_stats():
    """Show memory statistics."""
    agent = get_agent()
    memories = agent.memory.get_all()

    # Count by category
    categories = {}
    for m in memories:
        cat = m['category']
        categories[cat] = categories.get(cat, 0) + 1

    print(f"Bender Stats - {len(memories)} total memories")
    print("-" * 40)
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        bar = "█" * min(count, 30)
        print(f"  {cat:15} {count:4} {bar}")

def bender_categories():
    """List all categories."""
    agent = get_agent()
    memories = agent.memory.get_all()
    categories = set(m['category'] for m in memories)

    print("Bender Categories:")
    for cat in sorted(categories):
        count = sum(1 for m in memories if m['category'] == cat)
        print(f"  {cat} ({count})")

def bender_list(category: str = None):
    """List memories."""
    agent = get_agent()
    memories = agent.memory.get_all()

    if category:
        memories = [m for m in memories if m['category'] == category]

    print(f"Bender's memories ({len(memories)}):")
    for m in memories:
        print(f"  [{m['category']}] {m['content'][:80]}")

def bender_export():
    """Export all memories to JSON."""
    agent = get_agent()
    memories = agent.memory.get_all()

    export_path = os.path.expanduser("~/agent/bender_export.json")
    with open(export_path, 'w') as f:
        json.dump(memories, f, indent=2)

    print(f"Bender: Exported {len(memories)} memories to {export_path}")

def print_help():
    print("""
SuperBender - AI Memory Agent + Changelog Tracker

QUERY:
  bender "question"              Semantic search your knowledge base

STORE:
  bender learn "fact" [category] Store knowledge (default: learned)
  bender log "change details"    Log timestamped changelog entry

VIEW:
  bender changelog [n]           Show last n changelog entries
  bender today                   Show today's entries
  bender week                    Show this week's entries
  bender list [category]         List memories (optionally by category)
  bender stats                   Show memory statistics
  bender categories              List all categories

MANAGE:
  bender export                  Export all to JSON
  bender forget                  Clear all memories

CATEGORIES:
  changelog   - Pipeline changes with timestamps
  decisions   - Trade-offs and reasoning
  insights    - Performance discoveries
  bugs        - Issues and fixes
  scripts     - Script documentation
  pipeline    - Pipeline configuration
  learned     - General knowledge
""")

def main():
    if len(sys.argv) < 2:
        print_help()
        return

    cmd = sys.argv[1]

    if cmd in ["-h", "--help", "help"]:
        print_help()
    elif cmd == "learn" and len(sys.argv) >= 3:
        content = sys.argv[2]
        category = sys.argv[3] if len(sys.argv) > 3 else "learned"
        bender_learn(content, category)
    elif cmd == "log" and len(sys.argv) >= 3:
        content = " ".join(sys.argv[2:])
        bender_log(content)
    elif cmd == "changelog":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        bender_changelog(limit)
    elif cmd == "today":
        bender_today()
    elif cmd == "week":
        bender_week()
    elif cmd == "stats":
        bender_stats()
    elif cmd == "categories":
        bender_categories()
    elif cmd == "list":
        category = sys.argv[2] if len(sys.argv) > 2 else None
        bender_list(category)
    elif cmd == "export":
        bender_export()
    elif cmd == "forget":
        agent = get_agent()
        agent.reset()
        print("Bender: Memory wiped!")
    else:
        # It's a question
        query = " ".join(sys.argv[1:])
        bender_ask(query)

if __name__ == "__main__":
    main()
