from contextlib import contextmanager
import errno
from io import StringIO
import os
from pathlib import Path
import re
import select
import signal
import subprocess
import sys
import time

import click
from click.testing import CliRunner
import pytest
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


def test_captured_output_retains_final_board_and_result(monkeypatch):
    """Keep the completed board and prompts readable without cursor controls."""
    result = invoke_game(monkeypatch, "cat", ["--player", "Solo"], "z\ncat\n")

    assert result.exit_code == 0
    assert result.output.count("HANGMAN // ROUND 01") == 1
    assert "WORD  C A T" in result.output
    assert "MISSES  1/8" in result.output
    assert "Solo's guess: z" in result.output
    assert "Solo's guess: cat" in result.output
    assert "Solo wins!" in result.output
    assert "\x1b[" not in result.output


def test_invalid_guess_feedback_remains_visible(monkeypatch):
    """Keep validation feedback in ordinary captured output."""
    result = invoke_game(monkeypatch, "cat", ["--player", "Solo"], "!\ncat\n")

    assert result.exit_code == 0
    assert "Enter a new letter or word." in result.output
    assert "Solo wins!" in result.output


@pytest.mark.filterwarnings("error::DeprecationWarning")
def test_redirected_input_does_not_use_cursor_positioning(monkeypatch):
    """Use static output even if stdout supports interactive rendering."""
    monkeypatch.setattr(main, "Console", lambda: Console(force_terminal=True, force_interactive=True))

    result = invoke_game(monkeypatch, "cat", ["--player", "Solo"], "cat\n")

    assert result.exit_code == 0
    unstyled = re.sub(r"\x1b\[[0-9;]*m", "", result.output)
    assert "\x1b[" not in unstyled
    assert "WORD  C A T" in unstyled
    assert "Solo wins!" in unstyled


class TerminalScreen:
    """Interpret the cursor, erase, wrap, and scroll behavior used by Rich."""

    def __init__(self, columns: int, rows: int) -> None:
        """Create a blank normal screen with retained scrollback."""
        self.columns = columns
        self.rows = rows
        self.lines = [[" "] * columns for _ in range(rows)]
        self.history: list[str] = []
        self.x = 0
        self.y = 0
        self.cursor_visible = True

    def _newline(self) -> None:
        """Scroll at the bottom margin without discarding history."""
        self.y += 1
        if self.y == self.rows:
            self.history.append("".join(self.lines.pop(0)).rstrip())
            self.lines.append([" "] * self.columns)
            self.y -= 1

    def feed(self, output: str) -> None:
        """Apply terminal output, rejecting unsupported control sequences."""
        tokens = re.findall(r"\x1b\[[0-?]*[ -/]*[@-~]|[^\x1b]", output)
        for token in tokens:
            if token.startswith("\x1b["):
                self._control(token)
            elif token == "\r":
                self.x = 0
            elif token == "\n":
                self._newline()
            elif token == "\b":
                self.x = max(0, self.x - 1)
            elif token >= " ":
                if self.x == self.columns:
                    self.x = 0
                    self._newline()
                self.lines[self.y][self.x] = token
                self.x += 1

    def _control(self, token: str) -> None:
        """Apply the subset of CSI operations emitted by the CLI."""
        arguments, command = token[2:-1], token[-1]
        if command == "m":
            return
        if arguments == "?25" and command in "hl":
            self.cursor_visible = command == "h"
            return
        amount = int(arguments or "1")
        if command == "A":
            self.y = max(0, self.y - amount)
        elif command == "B":
            self.y = min(self.rows - 1, self.y + amount)
        elif command == "C":
            self.x = min(self.columns - 1, self.x + amount)
        elif command == "D":
            self.x = max(0, self.x - amount)
        elif command == "G":
            self.x = amount - 1
        elif command == "K":
            start = 0 if amount in (1, 2) else self.x
            end = self.x + 1 if amount == 1 else self.columns
            self.lines[self.y][start:end] = [" "] * (end - start)
        else:
            raise AssertionError(f"Unsupported terminal control: {token!r}")

    @property
    def text(self) -> str:
        """Return the visible screen without styling."""
        return "\n".join("".join(line).rstrip() for line in self.lines)

    @property
    def transcript(self) -> str:
        """Return scrollback and the visible screen together."""
        return "\n".join([*self.history, self.text])


class TerminalGame:
    """Drive the real CLI through a size-constrained pseudo-terminal."""

    def __init__(
        self, descriptor: int, process: subprocess.Popen[bytes], columns: int, rows: int
    ) -> None:
        """Retain the process and raw output needed for screen snapshots."""
        self.descriptor = descriptor
        self.process = process
        self.columns = columns
        self.rows = rows
        self.output = b""

    def read_until(self, marker: bytes) -> TerminalScreen:
        """Wait for fresh prompt/result output, then drain pending writes."""
        start = len(self.output)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            ready, _, _ = select.select([self.descriptor], [], [], 0.1)
            if ready:
                try:
                    data = os.read(self.descriptor, 65536)
                except OSError as error:
                    if error.errno != errno.EIO:
                        raise
                    break
                if not data:
                    break
                self.output += data
            elif marker in self.output[start:]:
                break
        assert marker in self.output[start:], self.output.decode(errors="replace")
        screen = TerminalScreen(self.columns, self.rows)
        screen.feed(self.output.decode())
        assert b"\x1b[?1049h" not in self.output
        return screen

    def guess(self, guess: str, marker: bytes = b"fred's guess") -> TerminalScreen:
        """Enter a guess and capture the next pending prompt or final result."""
        os.write(self.descriptor, guess.encode() + b"\n")
        return self.read_until(marker)


@contextmanager
def terminal_game(columns: int = 105, rows: int = 24):
    """Launch a deterministic game and always reap its process and descriptors."""
    pty = pytest.importorskip("pty")
    termios = pytest.importorskip("termios")
    master, slave = pty.openpty()
    process = None
    try:
        termios.tcsetwinsize(slave, (rows, columns))
        environment = dict(os.environ, TERM="xterm-256color")
        for name in ("COLUMNS", "LINES", "FORCE_COLOR", "NO_COLOR", "TTY_COMPATIBLE", "TTY_INTERACTIVE"):
            environment.pop(name, None)
        process = subprocess.Popen(
            [
                sys.executable, "-u", "-c",
                "import main; main.choose_word = lambda: 'cat'; "
                "main.main(['--player', 'fred'])",
            ],
            cwd=Path(main.__file__).parent,
            stdin=slave,
            stdout=slave,
            stderr=slave,
            env=environment,
        )
        os.close(slave)
        slave = -1
        yield TerminalGame(master, process, columns, rows)
    finally:
        if process is not None:
            if process.poll() is None:
                process.terminate()
            process.wait(timeout=5)
        os.close(master)
        if slave != -1:
            os.close(slave)


def test_interactive_board_updates_in_place_while_prompting():
    """Catch stacked frames while preserving the real prompt/guess transcript."""
    with terminal_game() as game:
        screen = game.read_until(b"fred's guess")
        assert screen.text.count("HANGMAN // ROUND 01") == 1
        assert "fred's guess:" in screen.text
        assert "MISSES  0/8" in screen.text

        screen = game.guess("z")
        assert screen.transcript.count("HANGMAN // ROUND 01") == 1
        assert screen.text.count("╭") == 1
        assert "MISSES  1/8    WRONG  z" in screen.text
        assert "fred's guess:" in screen.text
        assert "fred's guess: z" in screen.transcript

        screen = game.guess("!")
        assert screen.transcript.count("HANGMAN // ROUND 01") == 1
        assert "MISSES  1/8    WRONG  z" in screen.text
        assert "Enter a new letter or word." in screen.transcript
        assert "fred's guess:" in screen.text

        screen = game.guess("cat", b"fred wins!")
        assert game.process.wait(timeout=5) == 0
        assert screen.transcript.count("HANGMAN // ROUND 01") == 1
        assert "WORD  C A T" in screen.text
        assert "fred wins! The word was cat." in screen.text
        assert screen.cursor_visible
        for guess in ("z", "!", "cat"):
            assert f"fred's guess: {guess}" in screen.transcript


def test_interactive_board_remains_usable_in_small_terminal():
    """Keep input visible and stale board fragments out of a short screen."""
    with terminal_game(columns=80, rows=16) as game:
        screen = game.read_until(b"fred's guess")
        assert "fred's guess:" in screen.text
        for guess in ("z", "x", "!"):
            screen = game.guess(guess)
            assert screen.transcript.count("HANGMAN // ROUND 01") == 1
            assert screen.text.count("╭") == 1
            assert "fred's guess:" in screen.text

        screen = game.guess("cat", b"fred wins!")
        assert game.process.wait(timeout=5) == 0
        assert screen.transcript.count("HANGMAN // ROUND 01") == 1
        assert "fred wins! The word was cat." in screen.text
        assert screen.cursor_visible


def test_interactive_typing_and_scrollback_keep_only_the_current_board():
    """Keep the board visible during typing and preserve a long input history."""
    with terminal_game() as game:
        game.read_until(b"fred's guess")
        os.write(game.descriptor, b"z")
        screen = game.read_until(b"z")
        assert screen.text.count("HANGMAN // ROUND 01") == 1
        assert "fred's guess: z" in screen.text
        assert "MISSES  0/8" in screen.text

        os.write(game.descriptor, b"\n")
        game.read_until(b"fred's guess")
        for guess in ["", *(["!"] * 12)]:
            screen = game.guess(guess)
            assert screen.transcript.count("HANGMAN // ROUND 01") == 1
            assert "MISSES  1/8" in screen.text
            assert "fred's guess:" in screen.text

        screen = game.guess("cat", b"fred wins!")
        assert game.process.wait(timeout=5) == 0
        assert screen.transcript.count("HANGMAN // ROUND 01") == 1
        assert screen.transcript.count("Enter a new letter or word.") == 12
        assert screen.transcript.count("fred's guess: !") == 12
        assert "fred's guess: z" in screen.transcript


@pytest.mark.parametrize("interrupt", [False, True], ids=["eof", "interrupt"])
def test_interactive_abort_leaves_terminal_usable(interrupt):
    """Leave a visible cursor and readable board on both Click abort paths."""
    with terminal_game() as game:
        game.read_until(b"fred's guess")
        if interrupt:
            game.process.send_signal(signal.SIGINT)
        else:
            os.write(game.descriptor, b"\x04")
        screen = game.read_until(b"Aborted!")
        assert game.process.wait(timeout=5) == 1
        assert screen.transcript.count("HANGMAN // ROUND 01") == 1
        assert screen.cursor_visible


def test_interactive_loss_retains_final_board_and_result():
    """Update the same board through all misses and retain the losing result."""
    with terminal_game() as game:
        game.read_until(b"fred's guess")
        for guess in "bdefghi":
            screen = game.guess(guess)
            assert screen.transcript.count("HANGMAN // ROUND 01") == 1
        screen = game.guess("j", b"Out of guesses.")
        assert game.process.wait(timeout=5) == 0
        assert screen.transcript.count("HANGMAN // ROUND 01") == 1
        assert "MISSES  8/8" in screen.text
        assert "Out of guesses. The word was cat." in screen.text
        assert screen.cursor_visible
