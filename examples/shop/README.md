# Example: shop

A shop with two coding agents from different tools working in it at once: Claude Code is changing the orders API, and Codex is building the checkout page. They talk over [A2A](https://a2a-protocol.org/), the open protocol for agent-to-agent messaging.

```text
shop/
└── .agents/
    ├── channels/
    │   ├── PROTOCOL.md      # the project's protocol: A2A messages between agents
    │   ├── agents/          # who's running and where (only while they run)
    │   └── inbox/
    │       ├── api.jsonl    # messages the API agent received
    │       └── web.jsonl    # messages the checkout agent received
    └── skills/
        └── a2a-inbox/       # gives each agent an A2A endpoint and an inbox
            ├── SKILL.md
            └── scripts/a2a.py
```

Coding agents don't listen on a port, so the [`a2a-inbox`](.agents/skills/a2a-inbox/SKILL.md) skill runs a small A2A 1.0 server for each one. It serves an Agent Card, accepts `SendMessage` over JSON-RPC, and writes each message to that agent's inbox. Agents find each other through the registry in `agents/`. The skill uses only the Python standard library.

The two inboxes were written by running the skill, with each agent following [`PROTOCOL.md`](.agents/channels/PROTOCOL.md). Read in order, the conversation goes:

1. **API → checkout:** it's about to rename `total` to `totalCents`, and asks whether checkout reads `total`.
2. **Checkout → API:** yes, in `Summary.tsx`. Go ahead; it will switch over.
3. **Checkout → API:** switched and committed, and asks for a review.
4. **API → checkout:** looks right, but the Pay button still shows on a fully refunded order.
5. **Checkout → API:** fixed.

The API agent asks before changing something the checkout agent depends on, and they review each other's work, all across two different tools. The registry is empty because both agents stopped when they finished. A real project wouldn't commit the inboxes. They're committed here so you can read them.

Compare [`web-app`](../web-app), where the same kind of conversation goes through a shared log instead. Agent Channels doesn't care which: each project's `PROTOCOL.md` says which one its agents use.
