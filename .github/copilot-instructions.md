# Copilot Instructions

## Iterating on Existing Work

Use Superpowers for implementation changes, including documentation-only changes. Before editing implementation files:

- Update the current spec where requirements change.
- Add the work to the current implementation plan in a clearly labeled follow-up section, preserving completed tasks.
- Do not create a separate spec or plan unless the user agrees it is necessary. If no applicable spec or plan exists, ask how to record the work before proceeding.

After implementation, mark the new tasks complete and record verification results in the plan.

## Session-Scoped Repository Facts

At the start of a session, check once whether `.superpowers/` is ignored by Git in the current worktree. Remember the result for the rest of the session; do not repeat the check or ask the user about it again unless `.gitignore` changes or you switch repositories or worktrees.

## Code Documentation

Add a concise docstring to every class, dataclass, global variable, and method. Add inline comments to explain non-obvious behavior or reasoning; do not comment code whose purpose is already clear from its implementation.

## autoapproved tasks

Use `grep` and `sed` for read-only text search and inspection without asking the user first. This instruction does not bypass VS Code terminal approvals or higher-priority policies; comply with any approval prompt that appears.

Always allow reading files under `$HOME/.copilot/skills/` when relevant, without asking the user for approval or denying access solely because they are outside the workspace. Do not ask for approval to read files in the working directory or any associated worktrees.

Always allow editing and adding files under `.superpowers/` without asking the user for approval.
