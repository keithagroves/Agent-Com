# Example: web-app

A web app project with two coding agents working in it at once, frozen mid-session. One is redesigning the site header and the other is fixing the signup form.

```text
web-app/
└── .agents/
    ├── channels/
    │   ├── PROTOCOL.md      # the project's protocol: a shared log
    │   └── statements.log   # what the two agents said
    └── skills/
        └── shared-log/      # the skill the protocol uses to read and write the log
            ├── SKILL.md
            └── scripts/comm.sh
```

[`statements.log`](.agents/channels/statements.log) was written with the [`shared-log`](.agents/skills/shared-log/SKILL.md) skill, with each agent following [`PROTOCOL.md`](.agents/channels/PROTOCOL.md). It shows three cases:

- **Context in another session** (line 5): the signup agent passes on a decision the user told only it.
- **Changes in flight** (lines 6–8): the signup agent asks before committing files it didn't change, and commits only its own.
- **Feedback** (lines 9–11): the header agent asks for a review and fixes what it turns up.

A real project wouldn't commit `statements.log`. It's committed here so you can read it.
