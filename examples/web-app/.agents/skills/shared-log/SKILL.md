---
name: shared-log
description: Read and write a project's shared append-only agent log at .agents/communication/statements.log. Use when a project's Agent Com protocol says to use shared-log.
---

# Shared Log

A shared log is one file, `.agents/communication/statements.log`, that every agent in a project reads and appends to. This skill's `scripts/comm.sh` is the only way to touch it. The script takes a lock, so concurrent writes don't collide. A project's `PROTOCOL.md` decides what agents say in the log. This skill covers only how to read and write it.

## Commands

Run these from inside the project. `<skill-dir>` is the folder this file is in.

```bash
S=<skill-dir>/scripts/comm.sh

ID=$($S join "<what you're working on>" | cut -d' ' -f3)
$S say "$ID" "<statement>"   # refuses an ID that never joined
$S read [after]              # statements with a sequence number greater than <after>
```

`join` mints a random 8-hex-character ID and posts `joined: <what you're working on>`. Keep the ID for the rest of your session.

## Format

Each line is `<sequence> <timestamp> <id> <statement>`. The sequence number is the order; the timestamp is UTC and informational. A newline in a statement becomes a space.

## Where the log is

In a git repository the script uses the main checkout's log, so agents in different worktrees share one log. Outside git it uses `.agents/communication/statements.log` under the current directory. Set `AGENT_COMM_LOG` to another path for tests, never to a live log.

## Errors

- `has not joined`: you passed an ID that isn't in the log. Check it, or `join` again.
- `has been held for 10s`: another write may have died while holding the lock. Tell the user; don't remove the lock yourself.
