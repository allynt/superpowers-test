# Hangman Persistent-Board Regression Design

## Intent

Fix the repeated and partially stacked Hangman panels shown in the terminal during a round. The board should remain visible while players enter guesses, without sending the game to an alternate screen.

## Goals

- Keep one current board visible in a stable terminal region while the player enters a guess.
- Update that board in place after each valid guess; do not leave stale or partial board frames on screen.
- Keep prompts, entered guesses, invalid-input feedback, and the final result readable in the normal terminal and scrollback.
- Preserve current game rules, players, colors, board content, and result messages.

## Non-goals

- Do not change Hangman rules or the hot-pink palette.
- Do not use a full-screen/alternate-screen interface or add a dependency.
- Do not remove useful captured output in non-interactive terminals.

## Constraints

- Keep the change in the existing Click/Rich CLI.
- Interactive terminal behavior must be verified by observing the rendered screen after multiple prompts, not by counting redraw sequences in captured ANSI output.
- Restore terminal cursor/display state when the game exits, including an error path.
- Use Rich-supported terminal capabilities rather than adding OS-specific control sequences.
- For non-interactive output, retain readable Click prompts, the final board, and the result without attempting cursor positioning.
- Verify the interactive layout at approximately 105 columns by 24 rows, matching the supplied screenshot. Smaller or resized terminals may use Rich's existing overflow behavior, but input must remain usable and rendering must not leave stale board frames.

## Diagnosis

The CLI updates its board through Rich `Live`, but calls `click.prompt` while that live display is active. Click's prompt output is routed through Rich's console; Rich then prints that output above the live region and repositions the live renderable below it. A pseudo-terminal reproduction at the screenshot's approximate dimensions showed the same accumulated board frames. The issue is the interaction between prompt output and the live region, not the game-state update logic.

## Approaches

- **Stable board and separate prompt area (chosen):** Keep the normal terminal and scrollback, coordinate the board and input areas so prompts do not move or duplicate the board. This preserves the requested visible board and existing CLI feel, but requires careful terminal-aware rendering and input handling.
- **Temporarily hide the board during input:** Remove the live region before prompting and redraw it after the guess. This is simpler, but fails the requirement that the board stay visible while the player types.
- **Use an alternate screen:** Render the board and prompt in a full-screen view. It can provide a stable layout, but conflicts with the requested normal terminal/scrollback behavior and the existing no-alternate-screen constraint.

## Proposed behavior

The board occupies a stable region and remains visible while the active prompt and input are shown. Prompts, answers, and invalid-guess feedback remain readable in ordinary terminal output; historical board frames do not. Valid guesses update the same board region. Invalid input leaves the game state and board unchanged. On completion, leave the final board and print the existing win/loss result visibly.

The builder may choose the specific Rich or terminal-control mechanism, provided it meets these behaviors, adds no dependency, and restores terminal state reliably.

Non-interactive output does not need an in-place display; it should remain readable and include the final board and result. The supported interactive target is a terminal that Rich identifies as interactive and capable of cursor control. At smaller or resized dimensions, use Rich's normal overflow behavior while keeping input available and avoiding stale frames.

## Verification

Add a pseudo-terminal regression test that runs multiple guesses at a constrained terminal size and verifies the final visible screen has one current board, an active prompt while input is pending, and no stale board frames. Also verify invalid input, final win/loss output, non-interactive captured output, and existing game/CLI tests.
