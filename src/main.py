import click
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from game import GameState
from words import choose_word


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
    player_names = Text("PLAYERS  ", style="bold #45d6c6")
    for index, player in enumerate(game.players):
        if index:
            player_names.append(" / ", style="#6f8983")
        player_names.append(
            player,
            style="bold #45d6c6" if player == game.current_player else "#a4b8b2",
        )

    wrong = ", ".join(wrong_guesses) if wrong_guesses else "none"
    content = Group(
        player_names,
        Text(f"TURN  {game.current_player}", style="bold #d9ff70"),
        Text(""),
        Text(HANGMAN_STAGES[game.miss_count], style="#ff806b"),
        Text(f"WORD  {' '.join(game.masked_word.upper())}", style="bold #d9ff70"),
        Text(f"MISSES  {game.miss_count}/8    WRONG  {wrong}", style="#a4b8b2"),
    )
    return Panel(
        content,
        title=Text("HANGMAN // ROUND 01", style="bold #45d6c6"),
        border_style="#45d6c6",
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
                console.print(Text("Enter a new letter or word.", style="#ff806b"))
                continue

            if result.status == "incorrect":
                wrong_guesses.append(result.guess)

            live.update(_render_game(game, wrong_guesses))

    if game.winner is not None:
        console.print(Text(f"{game.winner} wins! The word was {game.word}.", style="bold #d9ff70"))
    else:
        console.print(Text(f"Out of guesses. The word was {game.word}.", style="bold #ff806b"))


if __name__ == "__main__":
    main()
