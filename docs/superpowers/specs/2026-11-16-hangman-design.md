# Hangman Game Design

## Intent
Build a fun solo or multiplayer terminal Hangman game as a hands-on way to learn the Superpowers workflow.

## Goals
- Let one or more named players guess a letter or the whole word; one player plays solo, while multiple players take turns.
- Draw one additional body part for each incorrect valid guess.
- End the single game immediately when a player solves the word or the drawing is complete; print a result and exit.
- Present the game in the selected Arcade Signal style using Rich.
- Keep game rules separate from the Click/Rich command-line interface.
- Keep future ideas in a root `TODO.md`, including evaluating Faker for random word generation and learning how to use Superpowers with subagents.

## Non-goals
- Replay, rounds, persistent scores, networking, or a full-screen Textual application.
- Using Faker in the first version; use a small curated built-in word list instead.

## Constraints
- Use the existing Python 3.13+ project.
- Add Click and Rich as dependencies; no additional word-generation dependency in the first version.
- Keep `.env` and other local secrets out of the committed project.

## Approaches
- **Single module:** simplest initially, but tangles game rules with terminal interaction.
- **Separate rules and CLI (chosen):** keeps the game logic testable and the Click/Rich presentation distinct, while remaining small enough for a learning project.
- **Textual app:** enables a full-screen interactive interface, but adds complexity that is unnecessary for this one-game terminal flow.

## Decisions and behavior
- The Click command accepts one or more player names; one name starts single-player mode, while two or more names start multiplayer mode and rotate turns after each valid guess.
- Correct letter guesses reveal every occurrence of that letter. A player wins when all letters are revealed or they guess the whole word correctly.
- Any incorrect letter or whole-word guess adds one body part. Repeated or malformed guesses are rejected without drawing a part or advancing the turn.
- Use eight ordered drawing stages, matching the selected mockup's `3 / 8` counter. When the final stage is reached, print a loss message, reveal the word, and exit. On a win, name the player, print a success message, and exit.
- Use a built-in curated list and choose a word randomly. Add a TODO noting that Faker could be evaluated later, including its tradeoff of adding a dependency and less predictable vocabulary.
- Use Rich for the cyan/lime-on-dark Arcade Signal display and Click for command parsing and prompts. Keep the game rules in a separate module from the CLI; exact module names and the command invocation are implementation details for the plan.

## Remaining to the builder
Choose a compact curated word list, define the ordered body-part drawing, and write focused tests for single-player flow, multiplayer turn order, guesses, win/loss conditions, and input validation.
