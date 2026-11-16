from typing import Final

import click
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from game import GameState
from words import choose_word


HOT_PINK: Final[str] = "#ff69b4"
"""Primary accent for the board and active player."""

LIGHT_PINK: Final[str] = "#ffb6c1"
"""Emphasis color for turn and word information."""

ERROR_PINK: Final[str] = "#ff5c8a"
"""Error color for the drawing and invalid or losing feedback."""

SUCCESS_LIME: Final[str] = "#d9ff70"
"""Success color for a winning result."""

MUTED_TEXT: Final[str] = "#a4b8b2"
"""Neutral color for secondary text."""

SEPARATOR_TEXT: Final[str] = "#6f8983"
"""Neutral color for separators between player names."""


HANGMAN_STAGES = (
    "  +---+\n  |   |\n      |\n      |\n      |\n========",
    "  +---+\n  |   |\n  O   |\n      |\n      |\n========",
    "  +---+\n  |   |\n  O   |\n  |   |\n      |\n========",
    "  +---+\n  |   |\n  O   |\n /|   |\n      |\n========",
    "  +---+\n  |   |\n  O   |\n /|\\  |\n      |\n========",
    "  +---+\n  |   |\n  O   |\n /|\\  |\n /    |\n========",
    "  +---+\n  |   |\n  O   |\n /|\\  |\n / \\  |\n========",
    "  +---+\n  |   |\n  O   |\n /|\\  |\n / \\  |\n_/    |\n========",
    "  +---+\n  |   |\n  O   |\n /|\\  |\n / \\  |\n_/  \\_|\n========",
)
"""Hangman drawings indexed by the number of misses."""


def _render_game(game: GameState, wrong_guesses: list[str]) -> Panel:
    """Build the panel for the current round state."""
    player_names = Text("PLAYERS  ", style=f"bold {HOT_PINK}")
    for index, player in enumerate(game.players):
        if index:
            player_names.append(" / ", style=SEPARATOR_TEXT)
        player_names.append(
            player,
            style=f"bold {HOT_PINK}" if player == game.current_player else MUTED_TEXT,
        )

    wrong = ", ".join(wrong_guesses) if wrong_guesses else "none"
    content = Group(
        player_names,
        Text(f"TURN  {game.current_player}", style=f"bold {LIGHT_PINK}"),
        Text(""),
        Text(HANGMAN_STAGES[game.miss_count], style=ERROR_PINK),
        Text(f"WORD  {' '.join(game.masked_word.upper())}", style=f"bold {LIGHT_PINK}"),
        Text(f"MISSES  {game.miss_count}/8    WRONG  {wrong}", style=MUTED_TEXT),
    )
    return Panel(
        content,
        title=Text("HANGMAN // ROUND 01", style=f"bold {HOT_PINK}"),
        border_style=HOT_PINK,
        padding=(1, 2),
    )


@click.command()
@click.option("--player", "players", multiple=True, required=True, metavar="NAME")
def main(players: tuple[str, ...]) -> None:
    """Run one Hangman round for the supplied players."""
    game = GameState(choose_word(), players)
    console = Console()
    wrong_guesses: list[str] = []

    with Live(_render_game(game, wrong_guesses), console=console) as live:
        while not game.finished:
            guess = click.prompt(f"{game.current_player}'s guess", type=str)
            result = game.submit_guess(guess)

            if result.status == "invalid":
                console.print(Text("Enter a new letter or word.", style=ERROR_PINK))
                continue

            if result.status == "incorrect":
                wrong_guesses.append(result.guess)

            live.update(_render_game(game, wrong_guesses))

    if game.winner is not None:
        console.print(Text(f"{game.winner} wins! The word was {game.word}.", style=f"bold {SUCCESS_LIME}"))
    else:
        console.print(Text(f"Out of guesses. The word was {game.word}.", style=f"bold {ERROR_PINK}"))


if __name__ == "__main__":
    main()
