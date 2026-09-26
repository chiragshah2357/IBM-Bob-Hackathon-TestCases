# TICKET-009: Human-readable task summary

## Summary

Add `Task.summary() -> str`.

## Acceptance criteria

- Format: `[x] #<id> <title> (P<priority>)` when done, `[ ]` when not done.
- If there is a due date, append it: `(P2, due 2026-10-01)`.
- Tests for done/not done and with/without due date.
