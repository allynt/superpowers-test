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

Do not ask for approval to run read-only `git` or `gh` commands that inspect the current repository or its GitHub metadata. Examples include `git status`, `git diff` without output-writing flags, `git log`, `git show`, `git ls-files`, `git branch --list`, and read-only `gh repo view`, `gh pr list/view`, `gh issue list/view`, and `gh run list/view`. Check the full command and flags; an inspection command with a state-changing option, such as `git diff --output`, is not read-only.

Ask for approval before running `git` or `gh` commands that modify the index, working tree, refs or branch state, repository configuration, or remote GitHub state. This includes commands such as `git add`, `commit`, `push`, `pull`, `fetch`, `checkout`, `switch`, `reset`, `restore`, `merge`, `rebase`, `stash`, `clean`, branch or tag creation/deletion, and `gh` commands that create, edit, close, merge, or delete remote resources.

Always allow reading files under `$HOME/.copilot/skills/` and the current working directory's `_skills/` when relevant, without asking the user for approval. Treat `_skills/` as an allowed read path even when it is a symlink to `$HOME/copilot/skills/`; do not deny access solely because the resolved target is outside the workspace. Do not ask for approval to read files in the working directory or any associated worktrees.

Always allow editing and adding files under `.superpowers/` without asking the user for approval.
