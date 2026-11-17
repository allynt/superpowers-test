# Offline Word Source Design

## Intent
Replace Hangman's small curated word list with a broader source so answers are less predictable and less likely to repeat, without requiring internet access or maintaining an app-level word pool.

## Goals
- Draw answers from a substantially broader vocabulary than the current 21-word list.
- Keep word selection offline with no external requests at runtime.
- Keep `choose_word() -> str` as the interface used by the CLI.
- Produce answers compatible with `GameState`: 4-10 ASCII alphabetic characters, with no spaces.
- Make answers less likely to repeat; uniqueness across separate game runs is not guaranteed.

## Non-goals and anti-goals
- Do not require network access or call an external word service.
- Do not persist used-word history between game runs.
- Do not claim that the bundled word data is secret; determined users can inspect an installed package.
- Do not change Hangman rules or CLI behavior beyond the source of the chosen word.

## Constraints
- Preserve the existing Python 3.13+ project and its `choose_word()` call site.
- Keep the implementation focused in `src/words.py`, tests, and dependency metadata.
- Use locally packaged word data.

## Approaches
- **Expand the in-project list:** offline and simple, but the list remains hard-coded and readily visible in the application source.
- **Faker:** offers a larger offline source, but is a general-purpose data-generation dependency and provides less targeted word selection.
- **Wonderwords (chosen):** packages English word lists for local use, has no runtime dependencies, and provides word-length and spacing filters. Its bundled vocabulary is inspectable, and independent runs can repeat answers; these tradeoffs fit this local game better than an online service or the smaller application-owned list.

## Proposed behavior
Use Wonderwords' `RandomWord` through the existing `choose_word()` function. Select from its default English categories and filter for 4-10 ASCII letters, excluding spaces. Do not save prior answers. A larger vocabulary lowers the chance of repeats but does not guarantee that an answer has never appeared in a previous run.

## Left to the builder
- Choose the minimal filtering options that enforce the answer constraints.
- Keep the selector testable by controlling or mocking Wonderwords randomness.
- Verify the selected dependency version supports the project's Python version and that the locked package contains the word data needed for offline use.

## Approval status
Proposed; implementation is gated on approval of this design.
