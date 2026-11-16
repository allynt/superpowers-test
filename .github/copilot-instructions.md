# Copilot Instructions

## Skills

Before starting a task, inspect `~/.copilot/skills/` and identify the skills relevant to the request. Read each relevant skill's full `SKILL.md` before acting, and follow its workflow. Do not load unrelated skills. If the directory or a relevant skill cannot be accessed, state that limitation and do not claim the skill was used.

## Session-Scoped Repository Facts

At the start of a session, check once whether `.superpowers/` is ignored by Git in the current worktree. Remember the result for the rest of the session; do not repeat the check or ask the user about it again unless `.gitignore` changes or you switch repositories or worktrees.

## autoapproved tasks

Use `grep` and `sed` for read-only text search and inspection without asking the user first. This instruction does not bypass VS Code terminal approvals or higher-priority policies; comply with any approval prompt that appears.
