# Agent Com

**Status:** Draft, v1

A project tells coding agents how to communicate with each other in one file, inside a folder set aside for agent communication:

```text
my-project/
├── .agents/
│   └── communication/
│       ├── PROTOCOL.md   # how agents in this project communicate
│       └── ...           # anything the protocol uses, such as a log
├── src/
└── AGENTS.md
```

Agent Com standardizes where that file is, not what it says. The protocol may use a log, mailboxes, a database, a local service, or anything else.

This repository follows Agent Com itself. Its [`PROTOCOL.md`](.agents/communication/PROTOCOL.md) is a small example: the team rules for a shared append-only log, which agents read and write with the [`shared-log`](skills/shared-log/SKILL.md) skill.

## Purpose

Coding agents often work concurrently in the same project, and they run into each other. Three typical cases:

- **Changes in flight.** An agent finishes its work and goes to commit, but `git status` shows changes to `Navigation.tsx` and `Footer.tsx` that it didn't make. Another agent is probably mid-edit. The first agent can't ask whether those changes are finished, whether they belong in this commit, or whether it should wait.
- **Context in another session.** One agent knows something the others need: a decision the user made, a bug it found, a plan it agreed on. The user wants the agents to stay aligned, but each session sees only its own conversation, so the user has to repeat it in each one.
- **Feedback.** The user wants one agent to review another's plan, diff or design. The user copies the work from one session into the other, then copies the feedback back.

Without a way to talk, agents guess, or the user carries messages between them. Many tools let agents talk to each other, but each in its own way, and often only with agents of the same tool. A project may have Claude Code in one terminal and Codex in another. Agent Com gives every project one place to say how its agents talk, and any agent that can read a file can find it.

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

Any other fields are optional, and agents ignore fields they don't understand. The Markdown body must describe the protocol or name what implements it. If the protocol depends on a skill, command, service or anything else outside the file, the body names each dependency and says how to get it. An agent that can't satisfy a dependency doesn't fall back to some other mechanism.

The format is compatible with Agent Skills (`SKILL.md`), so a runtime that loads skills can load `PROTOCOL.md` unchanged. A `PROTOCOL.md` is still not a skill: it records the protocol the project has chosen, not a reusable capability.

## Trust

Agents treat `PROTOCOL.md` like any other instructions found in a repository, including any commands it asks them to run.

## Why not a skill?

A skill teaches an agent how to use a communication mechanism. It doesn't tell the agent which mechanism a particular project uses. An agent with five communication skills installed still can't tell which one the other agents in this project are using. `PROTOCOL.md` tells it.

The two work together. A `PROTOCOL.md` may tell agents to use a skill, command, service or any other implementation. `PROTOCOL.md` also comes with the project when it's cloned, so an agent doesn't need to know in advance which skill to install.

## Why not AGENTS.md?

AGENTS.md holds instructions that every agent needs in every session. A communication protocol is needed only when agents coordinate, and it can be long. Putting it in AGENTS.md would load it into every session's context.

A separate file also has a fixed path and a clear owner. A coordination tool can create, detect or replace `PROTOCOL.md` without editing a file people wrote by hand, and an agent doesn't have to search free-form instructions for the part about other agents. AGENTS.md files can be nested, with the nearest one applying in each directory, but agents working in different parts of a project still need one shared protocol.

The two work together. AGENTS.md can point to the protocol, for example: `To coordinate with other agents, follow .agents/communication/PROTOCOL.md.` Agents that read AGENTS.md then know the protocol exists without loading it every session.

## Why a communication folder?

- **One place to look.** An agent asked to coordinate doesn't have to guess which tool a project uses. It checks one path.
- **A home for shared state.** Logs, mailboxes, locks and databases live next to the protocol that owns them instead of scattered across the project.
- **Easy to manage.** A user can inspect, ignore, back up or clear all agent communication by handling one folder.
## Not defined

Agent Com does not define identity, message format, transport, locking, liveness, claims, where shared state lives, whether any of it is committed, or any runtime's API. Those belong to the protocol and the project.