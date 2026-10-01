# Agent Com

**Status:** Draft, v1

A project tells coding agents how to communicate with each other in one file:

```text
.agents/communication/PROTOCOL.md
```

Agent Com standardizes where that file is, not what it says. The protocol may use a log, mailboxes, a database, a local service, or anything else.

## Purpose

Coding agents often work concurrently in the same project. They need a way to ask each other things like "I'm about to commit; should I include your changes?" Many tools solve this, each differently. Agent Com gives every project one place to say which approach it uses.

## The standard

1. A project that defines an agent communication protocol puts it in `.agents/communication/PROTOCOL.md`.
2. When asked to communicate or coordinate with other agents, an agent reads that file and follows it.
3. `PROTOCOL.md` is authoritative for agent communication in that project. Agents use only the mechanisms it describes and change shared state only in the ways it permits.

Reading the file is triggered by the user's request. A harness may be configured to have agents read it automatically.

If the file does not exist, Agent Com says nothing about how agents communicate in that project. Its absence does not mean no other agents are running.

## File format

`PROTOCOL.md` is Markdown with YAML frontmatter. Two fields are required:

```markdown
---
name: agent-file-communication
description: Coordinate agents through a shared append-only log.
---

# Agent File Communication

How to identify yourself, send messages, read messages, ...
```

- `name`: a stable identifier for the protocol.
- `description`: a short summary of what it does.

Any other fields are optional, and agents ignore fields they don't understand. Everything an agent needs to follow the protocol must be in the Markdown body.

This format is compatible with Agent Skills (`SKILL.md`), so a runtime that loads skills can load `PROTOCOL.md` unchanged.

## Trust

Agents treat `PROTOCOL.md` like any other instructions found in a repository, including any commands it asks them to run.

## Why a communication folder?

- **One place to look.** An agent asked to coordinate doesn't have to guess which tool a project uses. It checks one path.
- **A home for shared state.** Logs, mailboxes, locks and databases live next to the protocol that owns them instead of scattered across the project.
- **Easy to manage.** A user can inspect, ignore, back up or clear all agent communication by handling one folder.
- **Out of the way until needed.** Unlike a section in AGENTS.md, the protocol isn't loaded into every session's context, and tools can find it by path.

## Not defined

Agent Com does not define identity, message format, transport, locking, liveness, claims, where shared state lives, whether any of it is committed, or any runtime's API. Those belong to the protocol and the project.