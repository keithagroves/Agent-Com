# Example: web-app

A web app project with two coding agents working in it at once, frozen mid-session. One is redesigning the site header and the other is fixing the signup form.

```text
web-app/
└── .agents/
    └── communication/
        ├── PROTOCOL.md      # the project's protocol: a shared log
        └── statements.log   # what the two agents said
```

[`statements.log`](.agents/communication/statements.log) was written with the [`shared-log`](../../skills/shared-log/SKILL.md) skill, with each agent following [`PROTOCOL.md`](.agents/communication/PROTOCOL.md). It shows three cases:

- **Context in another session** (line 5): the signup agent passes on a decision the user told only it.
- **Changes in flight** (lines 6–8): the signup agent asks before committing files it didn't change, and commits only its own.
- **Feedback** (lines 9–11): the header agent asks for a review and fixes what it turns up.

A real project wouldn't commit `statements.log`. It's committed here so you can read it.
