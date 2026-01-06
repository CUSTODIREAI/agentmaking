# SuperBender - AI Memory Agent + Changelog Tracker

Central brain for knowledge, insights, and pipeline evolution tracking with semantic search.

## Quick Install (Any Linux)

```bash
curl -sL https://raw.githubusercontent.com/CUSTODIREAI/agentmaking/main/install.sh | bash
```

Or manually:
```bash
git clone https://github.com/CUSTODIREAI/agentmaking.git ~/agent
cd ~/agent && ./install.sh
```

## Features

- **Semantic Search** - Find related memories even with different wording
- **Changelog Tracking** - Log pipeline changes with timestamps
- **Time Views** - See today's or this week's entries
- **Categories** - Organize by type (changelog, decisions, insights, bugs...)
- **Statistics** - Visual breakdown of your knowledge base
- **Export** - Backup to JSON

## Installation

```bash
# Install dependencies
pip install sentence-transformers numpy

# Clone and install
git clone https://github.com/CUSTODIREAI/agentmaking.git ~/agent
sudo ln -sf ~/agent/bender.py /usr/local/bin/bender
sudo chmod +x /usr/local/bin/bender
```

## Usage

### Query (Semantic Search)
```bash
bender "how to fix CUDA OOM"
bender "why do we skip many faces"
bender "docker command for pipeline"
```

### Store Knowledge
```bash
bender learn "RTX 4090 has 24GB VRAM" facts
bender learn "Max 20 containers safe" pipeline
bender learn "Client prefers 1080p" clients
```

### Log Changes (Auto-Timestamped)
```bash
bender log "screen_shots.py: Added max_faces=5 filter to skip crowd scenes"
bender log "Increased batch size from 10 to 20 after OOM fix"
bender log "Rolled back face threshold from 0.7 to 0.6"
```

### View History
```bash
bender changelog        # Last 10 changes
bender changelog 20     # Last 20 changes
bender today            # Today's entries
bender week             # This week's entries
```

### Statistics & Categories
```bash
bender stats            # Visual breakdown
bender categories       # List all categories
bender list changelog   # All changelog entries
```

### Manage
```bash
bender export           # Export to JSON
bender forget           # Clear all (careful!)
```

## Categories

| Category | Purpose |
|----------|---------|
| `changelog` | Pipeline changes with timestamps |
| `decisions` | Trade-offs and reasoning |
| `insights` | Performance discoveries |
| `bugs` | Issues found and fixes |
| `scripts` | Script documentation |
| `pipeline` | Configuration & settings |
| `commands` | Useful commands to remember |
| `learned` | General knowledge |

## Example: Track Pipeline Evolution

```bash
# Log a change with full context
bender log "screen_shots.py: Added crowd detection (max_faces=5)"

bender learn "CHANGE 2026-01-06: screen_shots.py
PROBLEM: 14-face videos load 14 InsightFace models = OOM
SOLUTION: Skip frames with >5 faces, reject if >50% frames skipped
IMPACT: 3% videos skipped, 10x faster processing" changelog

# Query later
bender "why skip many faces"
bender "what changed in screen_shots"
```

## Sync Across Machines

```bash
# Push changes
cd ~/agent && git add -A && git commit -m "Update memories" && git push

# Pull on another machine
cd ~/agent && git pull
```

## Files

| File | Description |
|------|-------------|
| `bender.py` | CLI tool (symlinked to /usr/local/bin/bender) |
| `memory_agent.py` | Core semantic search engine |
| `memories/memory.db` | SQLite database |
| `memories/embeddings.json` | Vector embeddings cache |

## Architecture

```
Query → Sentence Transformer → Cosine Similarity → Top Results
         (all-MiniLM-L6-v2)      (semantic match)
```

Uses SQLite FTS5 for keyword search + sentence-transformers for semantic search, combining both for best results.

## License

MIT
