# Bender - AI Memory Agent

Local AI agent with semantic search memory capabilities.

## Features

- **SQLite + FTS5** for full-text search
- **Semantic search** using sentence-transformers (all-MiniLM-L6-v2)
- **Memory categories**: preferences, facts, schedule, context, learned
- **CLI interface** for quick access

## Installation

```bash
# Install dependencies
pip install sentence-transformers numpy

# Install CLI
sudo cp bender.py /usr/local/bin/bender
sudo chmod +x /usr/local/bin/bender
```

## Usage

```bash
# Ask a question (semantic search)
bender "how many containers safe?"
bender "GPU memory"

# Teach something new
bender learn "RTX 4090 has 24GB VRAM" facts
bender learn "20 containers max for pipeline" learned

# List all memories
bender list

# List by category
bender list facts

# Clear all memories
bender forget
```

## Files

| File | Description |
|------|-------------|
| `memory_agent.py` | Core memory agent with SQLite + semantic search |
| `bender.py` | CLI wrapper |
| `monitor_pipeline.sh` | Background monitoring script |
| `PERMISSIONS.md` | Claude Code permissions guide |
| `AGENT_MEMORY.md` | AI agent memory implementation guide |

## Memory Storage

Memories stored in `~/agent/memories/`:
- `memory.db` - SQLite database with FTS5
- `embeddings.json` - Vector embeddings cache

## Example: Pipeline Monitoring

The agent can store knowledge about your pipeline and answer questions:

```bash
# Store pipeline knowledge
bender learn "Max 20 containers for 24GB VRAM" pipeline
bender learn "Use v4.8-cu130 for CUDA 13.0" pipeline
bender learn "OOM at 21GB+ VRAM usage" troubleshooting

# Query later
bender "containers VRAM"
# Returns: Max 20 containers for 24GB VRAM (87%)
```

## Autonomous Monitoring Workaround

Since Claude sub-agents fail for long tasks, use shell scripts:

```bash
nohup /tmp/monitor_pipeline.sh > /dev/null 2>&1 &
cat /tmp/monitor_pipeline.log
```

See `PERMISSIONS.md` for full Claude Code configuration.

## License

MIT
