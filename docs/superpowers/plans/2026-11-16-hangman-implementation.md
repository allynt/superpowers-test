# Hangman Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a fun one-round Hangman game with solo and multiplayer terminal play, a Rich Arcade Signal display, and Click command-line options.

**Architecture:** Keep deterministic game state and guess rules in `src/game.py`, and word selection in `src/words.py`. Use the existing `src/main.py` as the Click command and Rich presentation layer, with pytest coverage for game rules, word selection, and CLI behavior.

**Tech Stack:** Python 3.13+, uv, Click, Rich, pytest, and the Python standard library `random` module.

**Spec:** `docs/superpowers/specs/2026-11-16-hangman-design.md`

## Global Constraints

- Use the existing Python 3.13+ project.
- Require pytest 9 or newer to use native TOML configuration in `pyproject.toml`.
- Add Click and Rich as dependencies; no additional word-generation dependency in the first version.
- Use a small curated built-in word list instead of Faker in the first version.
- The Click command accepts one or more player names; one name starts single-player mode, while two or more names start multiplayer mode and rotate turns after each valid guess.
- Use eight ordered drawing stages; each incorrect valid guess adds one body part.
- A player wins when all letters are revealed or they guess the whole word correctly; on a win, name the player, print a success message, and exit.
- When the final stage is reached, print a loss message, reveal the word, and exit.
- Keep `.env` and other local secrets out of the committed project.

## Review Focus

- A single player should remain the active player after a valid nonterminal guess: `test_single_player_keeps_turn_after_valid_guess` in Task 1.
- Repeated letters in the secret should all be revealed by one case-insensitive letter guess: `test_letter_guess_reveals_every_occurrence` in Task 1.
- Repeated or malformed guesses should neither add a miss nor advance a multiplayer turn: `test_invalid_guess_does_not_change_game_state` in Task 1.
- An incorrect whole-word guess should cost exactly one miss and rotate to the next player: `test_wrong_word_guess_costs_one_miss_and_rotates` in Task 1.
- The eighth wrong guess and a successful full-word guess should each end the CLI immediately with the correct result: `test_eighth_miss_reveals_word_and_exits` and `test_single_player_correct_word_prints_success_and_exits` in Task 3.

---

### Task 1: Implement Game Rules

**Files:**
- Modify: `pyproject.toml`
- Modify: `uv.lock`
- Create: `src/game.py`
- Create: `tests/test_game.py`

**Interfaces:**
- Produces `GameState(word: str, players: tuple[str, ...])`.
- `GameState` exposes `current_player: str`, `masked_word: str`, `miss_count: int`, `finished: bool`, and `winner: str | None`.
- `GameState.submit_guess(guess: str) -> GuessResult`; `GuessResult` exposes `status` (`"correct"`, `"incorrect"`, `"invalid"`, `"won"`, or `"lost"`), `player: str`, and normalized `guess: str`.

- [x] **Step 1: Add pytest 9 or newer as a development dependency**

Run: `uv add --dev 'pytest>=9'`

- [x] **Step 2: Configure pytest to import modules from `src/`**

Add `[tool.pytest]` with `pythonpath = ["src"]` in `pyproject.toml`.

- [x] **Step 3: Write game-rule tests**

- In `tests/test_game.py`, add tests named `test_new_game_masks_word_and_starts_first_player`, `test_single_player_keeps_turn_after_valid_guess`, `test_multiplayer_rotates_after_valid_guess`, `test_letter_guess_reveals_every_occurrence`, `test_correct_word_guess_wins_for_current_player`, `test_wrong_word_guess_costs_one_miss_and_rotates`, `test_invalid_guess_does_not_change_game_state`, and `test_eighth_miss_ends_game`. Cover case-insensitive guesses, repeated-letter words, a duplicate guess, a nonalphabetic guess, one-player and two-player states, and the eight-miss limit.

- [x] **Step 4: Run the game tests to verify they fail for the missing game module**

Run: `uv run --python 3.13 pytest -q tests/test_game.py`
Expected: collection fails because `game` does not exist yet.

- [x] **Step 5: Implement `GameState` and `GuessResult` in `src/game.py`**

Define `GuessStatus` as `Literal["correct", "incorrect", "invalid", "won", "lost"]` and `GuessResult` as a frozen dataclass with `status`, `player`, and normalized `guess`. Implement the interfaces above with an eight-miss limit. Invalid or repeated guesses do not consume a miss or change the turn. Every valid nonterminal guess advances to the next player (a one-player game naturally keeps the same player). An incorrect eighth guess sets the game to lost; a solved word records the current player as winner.

- [x] **Step 6: Run the game tests to verify they pass**

Run: `uv run --python 3.13 pytest -q tests/test_game.py`
Expected: all game tests pass.

### Task 2: Add Curated Word Selection

**Files:**
- Create: `src/words.py`
- Create: `tests/test_words.py`
- Create: `TODO.md`

**Interfaces:**
- Consumes: none from Task 1.
- Produces `WORDS: tuple[str, ...]` and `choose_word() -> str` in `src/words.py`.

- [x] **Step 1: Write a deterministic word-selection test**

In `tests/test_words.py`, add `test_choose_word_returns_a_curated_word`, patching `words.random.choice` to select a known entry and asserting that it is returned.

- [x] **Step 2: Run the word test to verify it fails for the missing word module**

Run: `uv run --python 3.13 pytest -q tests/test_words.py`
Expected: collection fails because `words` does not exist yet.

- [x] **Step 3: Implement curated words and random selection**

Add at least 20 common lowercase ASCII words, each 4-10 letters long, to `WORDS` and implement `choose_word()` using `random.choice`.

- [x] **Step 4: Run the word test to verify it passes**

Run: `uv run --python 3.13 pytest -q tests/test_words.py`
Expected: the word-selection test passes.

- [x] **Step 5: Record Faker as a future idea in `TODO.md`**

Add these two items:
- Evaluate Faker for random word generation, including that it adds a dependency and may produce less familiar vocabulary.
- Learn how to use Superpowers with subagents.

### Task 3: Add the Click/Rich Terminal Game

**Files:**
- Modify: `pyproject.toml`
- Modify: `uv.lock`
- Modify: `src/main.py`
- Modify: `README.md`
- Create: `tests/test_cli.py`

**Interfaces:**
- Consumes `GameState` from Task 1 and `choose_word()` from Task 2.
- Produces a Click command named `main`, accepting repeated `--player NAME` options, and runnable as `uv run python src/main.py --player NAME`.

- [x] **Step 1: Add Click and Rich dependencies**

Run: `uv add click rich`

- [x] **Step 2: Write CLI behavior tests**

In `tests/test_cli.py`, use `click.testing.CliRunner` and patch `main.choose_word`. Add tests named `test_single_player_correct_word_prints_success_and_exits`, `test_multiplayer_turn_rotates_after_wrong_guess`, `test_eighth_miss_reveals_word_and_exits`, and `test_player_option_is_required`. Assert a one-player game can finish, two players take turns, the loss reveals the chosen word, and the command exits without prompting for another round.

- [x] **Step 3: Run the CLI tests to verify they fail before implementation**

Run: `uv run --python 3.13 pytest -q tests/test_cli.py`
Expected: collection or invocation fails because the Click command and game UI are not implemented.

- [x] **Step 4: Implement the Click command and Rich presentation in `src/main.py`**

Use a required, repeatable `--player` option so one name selects solo play and multiple names select turn-based play. Use Rich to show the Arcade Signal palette (cyan/lime on dark, coral for misses), current player, masked word, wrong guesses, miss count out of eight, and the corresponding drawing stage. Prompt for one letter or whole-word guess at a time. Print the winner and success on a win, or a loss message and revealed word after the eighth miss, then return so the process exits.

- [x] **Step 5: Document installation and invocation in `README.md`**

Preserve existing README content and add the `uv sync` setup command, a single-player invocation, and a multiplayer invocation using repeated `--player` options.

- [x] **Step 6: Run the full test suite**

Run: `uv run --python 3.13 pytest -q`
Expected: all game, word-selection, and CLI tests pass.

---

### Task 4: Keep the Hangman Board Persistent (#3)

**Files:**
- Modify: `src/main.py`
- Test: `tests/test_cli.py`
- Spec: `docs/superpowers/specs/2026-11-16-hangman-design.md`

**Interfaces:**
- Consumes: `GameState` and the existing CLI behavior.
- Produces: `_render_game(game: GameState, wrong_guesses: list[str]) -> Panel`, used as the renderable for `rich.live.Live`.
- `main` creates a Rich `Live` display on every run, updates it after valid guesses, preserves Click prompts and invalid-guess feedback, and prints the final result after the live context exits.

**Review Focus:**
- Captured/non-terminal output still shows useful board snapshots and ordinary prompt/result text; test through `CliRunner` while asserting Rich `Live` is used.
- Invalid guesses preserve feedback and do not disrupt the next prompt; test invalid input followed by a winning guess.
- The final board update precedes the existing win/loss result; record Live updates, context exit, and result printing in order.
- Existing one-player and multiplayer rules remain unchanged; retain the current CLI and game-rule tests.

- [x] **Step 1: Add a CLI test for unconditional Live updates**

In `tests/test_cli.py`, add `test_live_display_updates_board_and_exits_before_result`. Mock `main.Live` and `main.Console`, then invoke the game through `CliRunner` with a wrong guess followed by a correct whole-word guess. Assert `Live` is constructed even for captured output, its update method receives both valid guesses, and its context exits before the winner is printed. Also add `test_invalid_guess_feedback_remains_visible_with_live_output`, using a malformed guess followed by a win and asserting the invalid-guess feedback and result remain visible.

- [x] **Step 2: Run the new test to verify it fails**

Run: `uv run --python 3.13 pytest -q tests/test_cli.py::test_live_display_updates_board_and_exits_before_result`
Expected: FAIL because the current CLI does not create or update a Rich `Live` display.

- [x] **Step 3: Refactor board rendering and add Rich Live in `src/main.py`**

Change `_render_game` to return a `Panel`. Create `Live` with the initial panel and existing `Console`; update it after each valid guess, including the terminal guess. Keep invalid-guess feedback outside the panel, and print the final result only after the Live context has exited. Do not add a TTY check or change game rules.

- [x] **Step 4: Verify CLI behavior and the full test suite**

Run: `uv run --python 3.13 pytest -q tests/test_cli.py tests/test_game.py`
Expected: all selected tests pass, including the Live update test and existing win/loss and multiplayer tests.

Run: `uv run --python 3.13 pytest -q`
Expected: all game, word-selection, and CLI tests pass.
Verification:
- The new Live lifecycle test failed before implementation because no Live display was created.
- `uv run --python 3.13 pytest -q tests/test_cli.py tests/test_game.py` — 14 passed.
- `uv run --python 3.13 pytest -q` — 15 passed.
- A real `CliRunner` invocation with Rich Live confirmed captured output includes the final Hangman board before the result.

---

### Task 5: Apply a Hot-Pink TUI Palette (#5)

**Files:**
- Modify: `src/main.py`
- Test: `tests/test_cli.py`
- Spec: `docs/superpowers/specs/2026-11-16-hangman-design.md`

**Interfaces:**
- Consumes: `_render_game(game: GameState, wrong_guesses: list[str]) -> Panel` and the existing CLI.
- Produces: named module-level palette constants used by all Rich UI styles in `src/main.py`.

**Review Focus:**
- Terminal renderers should show the specified hot pink and readable pink emphasis in truecolor output; test with `Console(force_terminal=True, color_system="truecolor")`.
- Error styling should remain visibly distinct from success styling; retain pink-red error and lime success colors.
- Existing captured output and game behavior must remain unchanged apart from color.

- [ ] **Step 1: Add a rendered-palette test**

Add `test_game_panel_uses_hot_pink_palette` to `tests/test_cli.py`, importing `StringIO` and `GameState` from `game`. Render `_render_game(GameState("cat", ("Solo",)), [])` through a `Console` backed by `StringIO`, with `force_terminal=True` and `color_system="truecolor"`. Assert output contains `38;2;255;105;180m`, `38;2;255;182;193m`, and `38;2;255;92;138m`, the ANSI truecolor values for hot pink `#ff69b4`, light pink `#ffb6c1`, and error pink `#ff5c8a`.

- [ ] **Step 2: Run the new test to verify it fails**

Run: `uv run --python 3.13 pytest -q tests/test_cli.py::test_game_panel_uses_hot_pink_palette`
Expected: FAIL because the current panel uses cyan, lime, and coral rather than the specified pink palette.

- [ ] **Step 3: Define and apply the named palette in `src/main.py`**

Define documented module-level constants for hot pink `#ff69b4`, light pink `#ffb6c1`, error pink `#ff5c8a`, success lime `#d9ff70`, and the existing muted/separator colors. Use the constants consistently for the panel border/title, player/turn/word text, drawing, invalid feedback, and win/loss result. Do not change text, layout, prompts, or game behavior.

- [ ] **Step 4: Run focused and full test suites**

Run: `uv run --python 3.13 pytest -q tests/test_cli.py`
Expected: all CLI tests pass, including the rendered-palette test.

Run: `uv run --python 3.13 pytest -q`
Expected: all tests pass.

- [ ] **Step 5: Record verification**

Record the focused and full-suite results in this follow-up section and mark completed steps.
