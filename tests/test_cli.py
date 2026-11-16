import click
from click.testing import CliRunner
import main


def invoke_game(monkeypatch, word, args, guesses):
    monkeypatch.setattr(main, "choose_word", lambda: word, raising=False)
    assert isinstance(main.main, click.Command)
    return CliRunner().invoke(main.main, args, input=guesses)


def test_single_player_correct_word_prints_success_and_exits(monkeypatch):
    result = invoke_game(monkeypatch, "cat", ["--player", "Solo"], "cat\n")

    assert result.exit_code == 0
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
