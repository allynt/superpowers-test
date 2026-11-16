# Repository Copilot Instructions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add concise repository-wide Copilot instructions that load relevant skills and permit read-only `grep`/`sed` use without bypassing VS Code approvals.

**Architecture:** Add one Markdown file at `.github/copilot-instructions.md`. Keep the instructions broad enough for the repository and easy to extend with future rules.

**Tech Stack:** Markdown; GitHub Copilot repository custom instructions.

**Spec:** `docs/superpowers/specs/2026-11-16-copilot-instructions-design.md`

## Global Constraints

- Use repository-wide instructions in `.github/copilot-instructions.md`.
- Check `~/.copilot/skills` and read relevant skills before acting; do not load unrelated skills.
- Do not ask the user before read-only `grep` or `sed` inspection, but do not claim or attempt to bypass VS Code terminal approval controls.
- Keep the instructions concise and extensible.

## Review Focus

- A relevant skill is available but not loaded: include a requirement to inspect the skills directory and read relevant `SKILL.md` files before acting.
- The skills directory is unavailable: do not claim skills were loaded; state the limitation and continue under available instructions.
- An unrelated skill exists: avoid requiring every skill to load on every task.
- A `grep` or `sed` invocation triggers platform approval: clarify that repository instructions do not bypass platform approvals.
- A command would modify files: limit the no-ask rule to read-only uses of `grep` and `sed`.

---

### Task 1: Add Repository Copilot Instructions

**Files:**
- Create: `.github/copilot-instructions.md`

**Interfaces:**
- Consumes: the agreed design in `docs/superpowers/specs/2026-11-16-copilot-instructions-design.md`.
- Produces: concise always-on repository instructions for skill discovery/loading and read-only `grep`/`sed` use.

- [ ] **Step 1: Create `.github/copilot-instructions.md`**

Include instructions to inspect `~/.copilot/skills/` for skills relevant to the current task, read each relevant skill's full `SKILL.md` before acting, and avoid loading unrelated skills. If the directory or a relevant skill cannot be accessed, require the agent to disclose that limitation rather than claim the skill was used. State that read-only `grep` and `sed` may be used without asking the user first, while any VS Code terminal approval prompt and higher-priority policy remain in force. Keep the file easy to extend with additional repository rules.

- [ ] **Step 2: Verify the instruction content**

Run: `grep -nE 'skills|SKILL\.md|grep|sed|approval' .github/copilot-instructions.md`
Expected: output shows the skill discovery/loading rule, the read-only command rule, and the approval limitation.

- [ ] **Step 3: Verify the custom-instructions file exists at the expected location**

Run: `test -f .github/copilot-instructions.md`
Expected: exit status 0.
