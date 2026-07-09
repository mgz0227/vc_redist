---
name: memory-setup
description: Enable and configure Moltbot/Clawdbot memory search for persistent context. Use when setting up memory, fixing "goldfish brain," or helping users configure memorySearch in their config. Covers MEMORY.md, daily logs, and vector search setup.
---

# Memory Setup Skill

Configure persistent memory for Moltbot/Clawdbot.

## Quick Setup

### 1. Enable Memory Search in Config

Add to `~/.clawdbot/clawdbot.json` or `moltbot.json`:

```json
{
  "memorySearch": {
    "enabled": true,
    "provider": "voyage",
    "sources": ["memory", "sessions"],
    "indexMode": "hot",
    "minScore": 0.3,
    "maxResults": 20
  }
}
```

### 2. Create Memory Structure

In your workspace, create:

```text
workspace/
├── MEMORY.md
└── memory/
    ├── logs/
    ├── projects/
    ├── groups/
    └── system/
```

### 3. Initialize MEMORY.md

Create `MEMORY.md` in workspace root:

```markdown
# MEMORY.md — Long-Term Memory

## About [User Name]
- Key facts, preferences, context

## Active Projects
- Project summaries and status

## Decisions & Lessons
- Important choices made
- Lessons learned

## Preferences
- Communication style
- Tools and workflows
```

## Config Options Explained

| Setting | Purpose | Recommended |
|---------|---------|-------------|
| `enabled` | Turn on memory search | `true` |
| `provider` | Embedding provider | `"voyage"` |
| `sources` | What to index | `["memory", "sessions"]` |
| `indexMode` | When to index | `"hot"` |
| `minScore` | Relevance threshold | `0.3` |
| `maxResults` | Max snippets returned | `20` |

### Provider Options

- `voyage` — Voyage AI embeddings
- `openai` — OpenAI embeddings
- `local` — Local embeddings, no API key needed

### Source Options

- `memory` — MEMORY.md plus memory/*.md files
- `sessions` — Past conversation transcripts
- `both` — Full context

## Daily Log Format

Create `memory/logs/YYYY-MM-DD.md` daily:

```markdown
# YYYY-MM-DD — Daily Log

## [Time] — [Event/Task]
- What happened
- Decisions made
- Follow-ups needed
```

## Agent Instructions

Add to AGENTS.md for agent behavior:

```markdown
## Memory Recall
Before answering questions about prior work, decisions, dates, people, preferences, or todos:
1. Run memory_search with relevant query
2. Use memory_get to pull specific lines if needed
3. If low confidence after search, say you checked
```

## Troubleshooting

### Memory search not working?

1. Check `memorySearch.enabled: true` in config.
2. Verify MEMORY.md exists in workspace root.
3. Restart gateway: `clawdbot gateway restart`.

### Results not relevant?

- Lower `minScore` to `0.2` for more results.
- Increase `maxResults` to `30`.
- Check that memory files have meaningful content.

### Provider errors?

- Voyage: set `VOYAGE_API_KEY` in environment.
- OpenAI: set `OPENAI_API_KEY` in environment.
- Use `local` provider if no API keys are available.

## Verification

Test memory is working:

```text
User: "What do you remember about [past topic]?"
Agent: should search memory and return relevant context.
```

If the agent has no memory, config is not applied. Restart the gateway.

## Full Config Example

```json
{
  "memorySearch": {
    "enabled": true,
    "provider": "voyage",
    "sources": ["memory", "sessions"],
    "indexMode": "hot",
    "minScore": 0.3,
    "maxResults": 20
  },
  "workspace": "/path/to/your/workspace"
}
```