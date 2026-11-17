# Offline Word Source Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Hangman's small curated word list with Wonderwords' broader, locally packaged vocabulary while preserving offline play and the existing selector interface.

**Architecture:** Keep `choose_word() -> str` in `src/words.py` as the boundary between the CLI and word selection. Use Wonderwords' `RandomWord` with constraints from the spec; leave game rules and CLI behavior unchanged.

**Tech Stack:** Python 3.13+, uv, Wonderwords, pytest.

**Spec:** `docs/superpowers/specs/2026-11-17-offline-word-source-design.md`

## Global Constraints

- Do not require network access or make external requests at runtime.
- Keep `choose_word() -> str` as the CLI's word-selection interface.
- Return 4-10 ASCII alphabetic characters with no spaces.
- Do not persist used-word history; repeats across separate game runs remain possible.
- Do not change Hangman rules or CLI behavior beyond the answer source.

## Review Focus

- A generated answer must satisfy the game's word constraints; pin the minimum and maximum lengths, ASCII letters, and exclusion of spaces in `test_choose_word_uses_wonderwords_filters` and `test_choose_word_returns_valid_word`.
- Word selection must remain fully local at runtime; use the package's bundled data and do not introduce network calls.
- Random selection must remain testable; replace the generator in the focused selector test instead of relying on a particular random result.
- Repeats across independent game runs are allowed; do not add persistent history or promise uniqueness.

---

### Task 1: Replace the Curated Selector

**Files:**
- Modify: `pyproject.toml`
- Modify: `uv.lock`
- Modify: `src/words.py`
- Modify: `tests/test_words.py`

**Interfaces:**
- Consumes: Wonderwords `RandomWord` and its bundled default English categories.
- Produces: `choose_word() -> str`, preserving the existing CLI call site.

- [ ] **Step 1: Write focused selector tests**

In `tests/test_words.py`, replace the curated-list test with `test_choose_word_uses_wonderwords_filters`. Monkeypatch `words.RandomWord` with a stub whose `word(**filters)` returns `"saffron"`, using `raising=False` because the attribute does not exist until implementation; assert the selector returns that value and requests minimum length 4, maximum length 10, `exclude_with_spaces=True`, and the ASCII-only regex `[A-Za-z]{4,10}`. Add `test_choose_word_returns_valid_word`, exercising the real selector and asserting the returned word is 4-10 ASCII letters with no spaces.

- [ ] **Step 2: Run the mocked test and confirm it fails**

Run: `uv run --python 3.13 pytest -q tests/test_words.py::test_choose_word_uses_wonderwords_filters`
Expected: FAIL because the current selector does not use Wonderwords or apply its filters.

- [ ] **Step 3: Add Wonderwords as a project dependency**

Run: `uv add wonderwords`.
Verify that the resolved release supports Python 3.13 and includes the word data as package resources; the game must not fetch vocabulary at runtime.

- [ ] **Step 4: Implement the Wonderwords selector**

In `src/words.py`, import `RandomWord` and implement `choose_word() -> str` using its default English categories with the exact filters asserted in the mocked test. Remove the embedded `WORDS` tuple and the `random` import. Do not retain or persist previously selected words.

- [ ] **Step 5: Run the focused word tests**

Run: `uv run --python 3.13 pytest -q tests/test_words.py`
Expected: both selector tests pass.

- [ ] **Step 6: Run the full test suite and record verification**

Run: `uv run --python 3.13 pytest -q`
Expected: all tests pass, with existing game and CLI behavior unchanged.
