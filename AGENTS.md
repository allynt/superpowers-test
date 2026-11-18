<!-- These instructions guide agent behavior; system and platform controls still apply. -->

# Agent Instructions

## Workspace Access

- Reading files in the current working directory and associated worktrees is allowed. Follow symlinks encountered there, including links to targets outside the workspace. This permission is read-only and does not authorize editing symlink targets.
- When relevant, reading files under `$HOME/.copilot/skills/` and the workspace `_skills/` directory is also allowed. Follow `_skills/` when it is a symlink, and do not deny access solely because its resolved target is outside the workspace.
- Adding or editing files under `.superpowers/` is allowed.

## Skill Discovery

- When a skill is required or requested, search relevant supported skill locations recursively for its `SKILL.md`, following symlinks to files and directories even when their targets are outside the workspace. Read the selected `SKILL.md` and any referenced instructions needed for the task; do not load unrelated skills.
- Do not treat a registered-skill list or search result as exhaustive if it may omit symlinked skills.
- "Superpowers" or "Superpowers skills" means the skills found recursively under `.github/skills/superpowers/`, including symlinked entries. Select the skills relevant to the task; the term does not mean invoking every skill or bulk-loading, unloading, or disabling them.

## Response Indicator

- Begin every user-facing response, including progress updates, with a compact Markdown skill indicator. Bold only the word `skill`; format each active skill name as inline code. Example: [**skill**: `agent-customization`].
- List only the skill(s) actually guiding that response, not every skill previously loaded. Use [**skill**: `none`] when no skill applies.
- Invoke required skills before displaying the indicator, and update it when the active skill changes. Do not use ANSI escape codes or HTML styling.

## Superpowers Specs and Plans

Before creating, revising, publishing, or resuming a specification or
implementation plan, invoke
[`superpowers-artifacts`](.github/skills/lfric/superpowers-artifacts/SKILL.md).
If invocation is unavailable, read its SKILL.md directly before proceeding.
Its storage and publication conventions override Superpowers defaults;
use it alongside the relevant Superpowers process skills.

## Git and GitHub Commands

- Read-only `git` and `gh` commands that inspect the current repository or GitHub metadata do not require approval. Examples include `git status`, `git diff` without output-writing flags, `git log`, `git show`, `git ls-files`, `git branch --list`, `gh pr view`, and `gh issue list`.
- Ask for approval before commands that modify the index, working tree, refs or branch state, repository configuration, or remote GitHub state. Examples include `git add`, `commit`, `fetch`, `pull`, `push`, `switch`, `merge`, `rebase`, `reset`, `restore`, `stash`, and `gh` commands that create, edit, close, merge, or delete remote resources.
- Classify the full command by its actual effects, including flags and aliases. A normally read-only command becomes state-changing if combined with a mutating option. For compound commands, ask for approval if any part changes state.