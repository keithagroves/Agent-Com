---
name: a2a-local
description: Coordinate with the other agents in this project by sending each other A2A messages.
---

# A2A Local

Every agent in this project runs its own A2A endpoint and has an inbox. Agents find each other through the registry in this folder and send messages directly. Nothing in this folder is committed.

## Requires: the a2a-inbox skill

Serve, send and read messages only with the `a2a-inbox` skill. It comes with this project, in [`.agents/skills/a2a-inbox`](../skills/a2a-inbox/SKILL.md). If your runtime hasn't loaded it, read its `SKILL.md` and run its script directly. It needs Python 3. If you can't run it, tell the user. Don't contact other agents any other way.

## Rules

1. **Serve first.** Start your endpoint before you start work, with a description of what you're doing. Then run `agents` to see who else is here.
2. **Ask the owner.** Before you change something another agent's description covers, or commit changes you didn't make, send that agent a message and wait for the answer.
3. **Check your inbox** before you commit and whenever you finish a step.
4. **No loops.** Only questions and requests expect a reply. End anything else with `No reply needed.` Never acknowledge an acknowledgement.
5. **Stop when you're done.** Run `stop`, so others don't message an agent that's gone.

Messages wait in an inbox until the recipient checks it. If you need an answer soon, say so to the user rather than assume it was seen.
