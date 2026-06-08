# AGENTS.md

This repo's agent instructions live in [`CLAUDE.md`](./CLAUDE.md) — read that
first. It describes the vault layout, the context-loading procedure, the skill
roster, and the rules every skill obeys.

This file exists so non-Claude agents (e.g. Codex) that look for `AGENTS.md`
find the same guidance. The conventions are identical; `CLAUDE.md` is canonical.

Quick orientation:

- **Capabilities are skills** under `.claude/skills/<name>/` — each is a
  `SKILL.md` plus optional `references/` and `scripts/`. Invoke one by name.
- **State is the vault** (`vault/`) — plain markdown the agents read and write.
- **Numbers come from the Python scripts**, never the model. Unavailable data is
  written `N/A`.
- **No secrets in the repo.** Credentials come from environment variables or a
  gitignored `.claude/settings.local.json`. Optional integrations (email,
  scheduling, push, dashboard) are documented in the README and can be deleted.
- **Not investment advice.** Every report says so.
