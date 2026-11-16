# Hangman Persistent-Board Regression Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Keep one Hangman board visible and updating in place while players enter guesses in a normal terminal.

**Architecture:** Keep the existing Click command, game state, and Rich-rendered board. Coordinate interactive input and board rendering so prompts and guesses remain in normal terminal scrollback without moving old board frames. Preserve readable captured output when cursor control is unavailable.

**Tech Stack:** Python 3.13+, Click, Rich, pytest, and Python standard-library pseudo-terminal support for regression testing.

**Spec:** `docs/superpowers/specs/2026-11-16-hangman-persistent-board-regression-design.md`

**Tracking issue:** #7

## Global Constraints

- Keep the change in the existing Click/Rich CLI.
- Use Rich-supported terminal capabilities rather than adding OS-specific control sequences.
- For non-interactive output, retain readable Click prompts, the final board, and the result without attempting cursor positioning.
- Verify the interactive layout at approximately 105 columns by 24 rows, matching the supplied screenshot. Smaller or resized terminals may use Rich's existing overflow behavior, but input must remain usable and rendering must not leave stale board frames.
- Preserve current game rules, players, colors, board content, and result messages.
- Do not use a full-screen/alternate-screen interface or add a dependency.

## Review Focus

- While input is pending, the current board and prompt must both be visible, with only one board frame: `test_interactive_board_updates_in_place_while_prompting`.
- After multiple valid guesses, the board must show current state without stale frames while prompts and typed guesses remain in scrollback: `test_interactive_board_updates_in_place_while_prompting`.
- Invalid input must leave game state and the board unchanged while preserving feedback: `test_interactive_board_updates_in_place_while_prompting`.
- At a smaller terminal size, input must remain usable and the board must not leave stale frames: `test_interactive_board_remains_usable_in_small_terminal`.
- Without an interactive terminal, the final board and result must remain readable: `test_captured_output_retains_final_board_and_result`.

---

### Task 1: Keep the Interactive Board in a Stable Terminal Region

**Files:**
- Modify: `src/main.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: `main` as the existing Click command and `_render_game(game: GameState, wrong_guesses: list[str]) -> Panel`.
- Produces: the same CLI interface and board content, with interactive prompts and board updates coordinated in the normal terminal; non-interactive output remains readable.

- [x] **Step 1: Add a pseudo-terminal screen helper and regression tests**

In `tests/test_cli.py`, add test-only helpers to run the Click command in a pseudo-terminal with a fixed size and read the currently rendered screen by interpreting Rich's cursor-positioning and erase sequences. Skip pseudo-terminal tests when the standard-library `pty` module is unavailable.

Add `test_interactive_board_updates_in_place_while_prompting`. Run a deterministic `cat` game as `fred` in a 105-by-24 terminal. At the initial prompt, assert that the prompt and one board are visible. Enter `z`; at the next prompt, assert that the same board region shows `MISSES 1/8` and exactly one board header is visible. Enter invalid `!`; assert that the board still shows `MISSES 1/8`, the invalid-input feedback is readable, and the prompt remains visible. Enter `cat`; assert the final board and `fred wins!` are visible, with no stale board frames. Also assert that prompts and entered guesses were emitted to normal terminal output.

Add `test_interactive_board_remains_usable_in_small_terminal` using an 80-by-16 pseudo-terminal. Assert the game continues to accept guesses, presents the active prompt, and does not leave duplicate or stale board frames.

Add `test_captured_output_retains_final_board_and_result` using `CliRunner` and a deterministic winning guess. Assert captured output includes the final board state and existing win message.

- [x] **Step 2: Run the new tests and confirm they expose the regression**

Run: `uv run --python 3.13 pytest -q tests/test_cli.py::test_interactive_board_updates_in_place_while_prompting tests/test_cli.py::test_interactive_board_remains_usable_in_small_terminal tests/test_cli.py::test_captured_output_retains_final_board_and_result`

Expected: both interactive screen assertions fail because prompts move the live region and leave old board frames visible; the captured-output assertion passes because Rich prints the final board when the live context closes.

- [x] **Step 3: Coordinate the input prompt and live board in `src/main.py`**

Keep the existing Click command signature, Rich board content, prompt text, invalid-input feedback, game rules, and result messages. Change only the interactive rendering/input flow so the board stays in one stable region while the active prompt is visible, and prompts/guesses remain ordinary terminal output. Use Rich-supported terminal behavior without adding a dependency or alternate screen. Preserve the existing readable non-interactive output path, and restore terminal display state when the command exits.

- [x] **Step 4: Run focused and full test suites**

Run: `uv run --python 3.13 pytest -q tests/test_cli.py`

Expected: all CLI tests pass, including the pseudo-terminal checks for stable rendering, invalid input, and captured output.

Run: `uv run --python 3.13 pytest -q`

Expected: all tests pass.

- [x] **Step 5: Record verification**

Record the focused and full-suite results in this task and mark completed steps.

## Follow-up: Issue #7 Execution and Verification

Implemented on `agents/the-tui-is-currently-doing-this-can-you`.

- Replaced the overlapping `Live`/Click prompt flow with synchronous `LiveRender` frames and Rich cursor controls. The board remains visible while input is pending; completed prompts and guesses are retained above the next frame.
- Reserved terminal space for input and its echoed newline, using Rich's vertical overflow for the smaller terminal.
- Kept static Click prompts, the completed board, and the result when either stream is non-interactive.
- Added real pseudo-terminal screen/scrollback assertions at 105-by-24 and 80-by-16. Additional coverage verifies active typing, empty input, repeated invalid guesses, scrolling history, loss, EOF, interrupt, and redirected stdin.
- Before the fix: the two interactive regression tests failed after the first guess with two board headers; the captured-output regression passed.
- Focused verification: `uv run --python 3.13 pytest -q tests/test_cli.py` -> **14 passed**.
- Full verification: `uv run --python 3.13 pytest -q` -> **23 passed**.
- Whitespace verification: `git diff --check` -> **passed**.
- Final review was a direct self-review of this small diff. No dependencies, alternate screen, game rules, palette, or result messages changed.
