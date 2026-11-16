from io import StringIO
from unittest.mock import MagicMock

import click
from click.testing import CliRunner
from rich.console import Console

import main
from game import GameState


def invoke_game(monkeypatch, word, args, guesses):
    monkeypatch.setattr(main, "choose_word", lambda: word, raising=False)
    assert isinstance(main.main, click.Command)
    return CliRunner().invoke(main.main, args, input=guesses)


def test_single_player_correct_word_prints_success_and_exits(monkeypatch):
    result = invoke_game(monkeypatch, "cat", ["--player", "Solo"], "cat\n")

    assert result.exit_code == 0
    assert "HANGMAN // ROUND 01" in result.output
    assert "WORD  C A T" in result.output
    assert "Solo wins!" in result.output
    assert "cat" in result.output


def test_multiplayer_turn_rotates_after_wrong_guess(monkeypatch):
    result = invoke_game(
        monkeypatch,
        "cat",
        ["--player", "Mira", "--player", "Eli"],
        "z\ncat\n",
    )

    assert result.exit_code == 0
    assert "Eli wins!" in result.output


def test_eighth_miss_reveals_word_and_exits(monkeypatch):
    result = invoke_game(
        monkeypatch,
        "abcdefgh",
        ["--player", "Solo"],
        "i\nj\nk\nl\nm\nn\no\np\n",
    )

    assert result.exit_code == 0
    assert "Out of guesses" in result.output
    assert "The word was abcdefgh." in result.output


def test_player_option_is_required():
    assert isinstance(main.main, click.Command)
    result = CliRunner().invoke(main.main, [])

    assert result.exit_code != 0
    assert "--player" in result.output


def test_game_panel_uses_hot_pink_palette():
    output = StringIO()
    console = Console(file=output, force_terminal=True, color_system="truecolor")

    console.print(main._render_game(GameState("cat", ("Solo",)), []))

    rendered = output.getvalue()
    assert "38;2;255;105;180m" in rendered
    assert "38;2;255;182;193m" in rendered
    assert "38;2;255;92;138m" in rendered


def test_live_display_updates_board_and_exits_before_result(monkeypatch):
    events = []
    live_context = mock_live_context(events)
    class RecordingConsole(Console):
        """Record printed results while preserving real console output."""

        def print(self, *args, **kwargs):
            """Record and print one renderable."""
            events.append(("print", args[0]))
            super().print(*args, **kwargs)

    def create_console():
        """Create a console that records user-visible messages."""
        return RecordingConsole()

    def create_live(*args, **kwargs):
        """Record Live construction and return its controlled context."""
        events.append(("live", args[0]))
        return live_context

    monkeypatch.setattr(main, "choose_word", lambda: "cat")
    monkeypatch.setattr(main, "Console", create_console)
    monkeypatch.setattr(main, "Live", create_live, raising=False)

    result = CliRunner().invoke(main.main, ["--player", "Solo"], input="z\ncat\n")

    assert result.exit_code == 0
    assert events[0][0] == "live"
    assert events[0][1].__class__.__name__ == "Panel"
    assert len([event for event in events if event[0] == "update"]) == 2
    assert events.index(("live-exit",)) < next(
        index for index, event in enumerate(events)
        if event[0] == "print" and "Solo wins!" in str(event[1])
    )
    assert "Solo wins!" in result.output


def test_invalid_guess_feedback_remains_visible_with_live_output(monkeypatch):
    monkeypatch.setattr(main, "choose_word", lambda: "cat")
    monkeypatch.setattr(main, "Live", lambda *args, **kwargs: mock_live_context([]), raising=False)

    result = CliRunner().invoke(main.main, ["--player", "Solo"], input="!\ncat\n")

    assert result.exit_code == 0
    assert "Enter a new letter or word." in result.output
    assert "Solo wins!" in result.output


def mock_live_context(events):
    """Return a context-manager mock that records board updates."""

    live_context = MagicMock()
    live_context.__enter__.side_effect = lambda: events.append(("live-enter",)) or live_context
    live_context.__exit__.side_effect = lambda *args: events.append(("live-exit",))
    live_context.update.side_effect = lambda renderable: events.append(("update", renderable))
    return live_context
