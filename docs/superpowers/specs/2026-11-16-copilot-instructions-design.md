# Repository Copilot Instructions Design

## Intent
Add a repository-specific starting point for Copilot guidance that can grow as additional rules are identified.

## Goals
- Add workspace-wide guidance in `.github/copilot-instructions.md`.
- Require checking `~/.copilot/skills` and reading the skills relevant to each task before acting.
- Allow read-only `grep` and `sed` inspection without asking the user first, while respecting any VS Code approval prompt that still appears.
- Keep the instruction concise and easy to extend.

## Non-goals
- Load every skill for every task, including unrelated skills.
- Change VS Code or terminal execution permission settings; repository instructions cannot override those controls.
- Add file-specific rules or user-wide preferences.

## Approaches
- **Repository-wide Copilot instructions (chosen):** `.github/copilot-instructions.md` applies to Copilot work throughout this repository and is simple to extend.
- **File-specific instructions:** useful for rules limited to matching files, but do not fit rules intended to apply across the repository.
- **User-level instructions:** reusable across workspaces, but not scoped to this repository.

## Constraints and decisions
The skills live in the current user's `~/.copilot/skills` directory. The instruction will tell Copilot to identify and load relevant skills, not every skill. The `grep`/`sed` rule can guide whether Copilot asks the user, but actual terminal approval remains controlled by VS Code.

## Builder calls
Use plain Markdown without frontmatter in `.github/copilot-instructions.md`; keep these initial rules short so later repository rules can be added cleanly.
