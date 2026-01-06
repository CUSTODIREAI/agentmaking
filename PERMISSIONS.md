# Claude Code Agent Permissions Guide

How to make Claude Code sub-agents run autonomously without permission prompts.

## The Problem

When spawning background agents via the `Task` tool, they fail with "prompts unavailable" and permissions get auto-denied:

```
auto-denied permission to use both the Write tool and the Bash tool
```

## The Solution

Configure `~/.claude/settings.local.json` with full permissions:

```json
{
  "permissions": {
    "defaultMode": "bypassPermissions",
    "allow": [
      "Read(/home/user/**)",
      "Read(/tmp/**)",
      "Write(/home/user/**)",
      "Write(/tmp/**)",
      "Bash(*)",
      "Bash(nvidia-smi:*)",
      "Bash(sudo docker:*)",
      "Bash(docker:*)",
      "Bash(python3:*)",
      "Bash(python:*)",
      "Bash(pip:*)",
      "Bash(ls:*)",
      "Bash(cat:*)",
      "Bash(grep:*)",
      "Bash(find:*)",
      "Bash(wc:*)",
      "Bash(head:*)",
      "Bash(tail:*)",
      "Bash(echo:*)",
      "Bash(date:*)",
      "Bash(sleep:*)",
      "Bash(chmod:*)",
      "Bash(mkdir:*)",
      "Bash(cp:*)",
      "Bash(mv:*)",
      "Bash(rm:*)",
      "Bash(git:*)",
      "Bash(gh:*)",
      "Bash(ssh:*)",
      "Bash(scp:*)",
      "Bash(rsync:*)",
      "Bash(curl:*)",
      "Bash(wget:*)",
      "Bash(nohup:*)",
      "Bash(ps:*)",
      "Bash(kill:*)",
      "Bash(pkill:*)",
      "Bash(xargs:*)",
      "Bash(bc:*)",
      "Bash(sshpass:*)",
      "Bash(aws:*)",
      "Bash(tailscale:*)"
    ],
    "deny": [],
    "ask": []
  },
  "sandbox": {
    "enabled": false,
    "autoAllowBashIfSandboxed": true,
    "allowUnsandboxedCommands": true
  }
}
```

### Key Settings

| Setting | Value | Purpose |
|---------|-------|---------|
| `defaultMode` | `"bypassPermissions"` | Skip all permission prompts |
| `Bash(*)` | Allow all | Wildcard for any bash command |
| `sandbox.enabled` | `false` | Disable sandboxing |
| `autoAllowBashIfSandboxed` | `true` | Auto-allow bash in sandbox |
| `allowUnsandboxedCommands` | `true` | Allow commands outside sandbox |

## Permission Modes

| Mode | Description |
|------|-------------|
| `default` | Prompts for permission on first use |
| `acceptEdits` | Auto-accepts file edits only |
| `dontAsk` | Executes without prompting |
| `bypassPermissions` | Bypasses ALL permission checks |
| `plan` | Read-only mode |

## Permission Syntax

### Bash Commands
```
"Bash(command:*)"     - Allow command with any args
"Bash(git log:*)"     - Allow git log with any args
"Bash(*)"             - Allow ALL commands (use with caution)
```

### File Access
```
"Read(/path/**)"      - Read all files in path
"Write(/path/**)"     - Write all files in path
"Read(*.ts)"          - Read all .ts files
"Write(src/**)"       - Write in src directory
```

## Known Limitations

1. **Sub-agents may still fail** for long-running tasks even with bypassPermissions
2. GitHub issue #5465 tracks this as an architectural limitation
3. **Best workaround**: Create shell scripts and run them via `nohup` in background

## Workaround: nohup Shell Script

For long-running autonomous tasks, create a shell script and run it in background:

```bash
# Create monitoring script
cat > /tmp/monitor_pipeline.sh << 'EOF'
#!/bin/bash
LOGFILE="/tmp/monitor_pipeline.log"
INTERVAL=120  # Check every 2 minutes
DURATION=7200 # Run for 2 hours

START_TIME=$(date +%s)
echo "=== Monitor Started: $(date) ===" >> "$LOGFILE"

while true; do
    NOW=$(date +%s)
    ELAPSED=$((NOW - START_TIME))

    if [ $ELAPSED -ge $DURATION ]; then
        echo "=== Monitor completed: $(date) ===" >> "$LOGFILE"
        break
    fi

    # Your monitoring commands here
    CONTAINERS=$(sudo docker ps -q | wc -l)
    GPU_UTIL=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits)

    echo "[$(date '+%H:%M:%S')] Containers: $CONTAINERS | GPU: ${GPU_UTIL}%" >> "$LOGFILE"

    sleep $INTERVAL
done
EOF

# Run in background
chmod +x /tmp/monitor_pipeline.sh
nohup /tmp/monitor_pipeline.sh > /dev/null 2>&1 &
echo "Monitor PID: $!"
```

Check status anytime:
```bash
cat /tmp/monitor_pipeline.log
```

## References

- [Claude Code Subagents Docs](https://code.claude.com/docs/en/sub-agents)
- [Permission Mode Guide](https://claudelog.com/faqs/how-to-set-claude-code-permission-mode/)
- [GitHub Issue #5465](https://github.com/anthropics/claude-code/issues/5465)
- [Sandboxing Docs](https://code.claude.com/docs/en/sandboxing)
