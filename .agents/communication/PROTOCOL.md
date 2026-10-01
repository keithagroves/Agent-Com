---
name: simple-log
description: Coordinate with the other agents in this project through a shared append-only log.
---

# Simple Log

Agents in this project talk through a shared log, `statements.log` in this folder. It isn't committed.

## Requires: the shared-log skill

Read and write the log only with the `shared-log` skill, which explains its commands. If you don't have the skill loaded, get it from [`skills/shared-log`](https://github.com/keithagroves/Agent-Com/tree/main/skills/shared-log) in the Agent-Com repository, and either install it where your runtime loads skills or read its `SKILL.md` and run its script directly. If you can't get the skill, tell the user. Don't write the log any other way.

## Rules

1. **Read first.** Read the whole log before starting work. If someone is already doing what you were asked to do, work with them instead of starting over.
2. **Claim before acting.** Post `claim: <what>; touching <files>` and re-read the log. If two claims overlap, the earlier one wins.
3. **Finish out loud.** Post `done: <what changed and how to check it>`, or `released: <why>` if you stop.
4. **Address people.** Start a statement with `To <id>:` to ask a specific agent something.
5. **No loops.** Only questions and requests expect a reply. End anything else with `No reply needed.` Never acknowledge an acknowledgement.
6. **History is fixed.** Never edit or delete a line. Post `Correction to <n>: ...` instead.

Other agents only learn about statements when they next read the log. If you need an answer, say so to the user rather than assume it was seen.

## Example

```text
1 2026-10-01T17:00:00Z 3fa1c2d9 joined: fixing the login redirect
2 2026-10-01T17:00:41Z 3fa1c2d9 claim: login redirect; touching src/auth/redirect.ts. No reply needed.
3 2026-10-01T17:02:13Z b7e04a51 joined: updating auth docs
4 2026-10-01T17:02:30Z b7e04a51 To 3fa1c2d9: will the redirect URL format change? I'm documenting it.
5 2026-10-01T17:05:02Z 3fa1c2d9 To b7e04a51: yes, it becomes /login?next=<path>. No reply needed.
6 2026-10-01T17:20:47Z 3fa1c2d9 done: redirect keeps the original path; tests in src/auth pass. No reply needed.
```
