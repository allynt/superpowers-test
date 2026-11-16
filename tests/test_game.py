from game import GameState


def test_new_game_masks_word_and_starts_first_player():
    game = GameState("puzzle", ("Mira", "Eli"))

    assert game.masked_word == "______"
    assert game.current_player == "Mira"
    assert game.miss_count == 0
    assert not game.finished
    assert game.winner is None


def test_single_player_keeps_turn_after_valid_guess():
    game = GameState("puzzle", ("Solo",))

    result = game.submit_guess("u")

    assert result.status == "correct"
    assert game.masked_word == "_u____"
    assert game.current_player == "Solo"


def test_multiplayer_rotates_after_valid_guess():
    game = GameState("cat", ("Mira", "Eli"))

    result = game.submit_guess("a")

    assert result.status == "correct"
    assert game.masked_word == "_a_"
    assert game.current_player == "Eli"


def test_letter_guess_reveals_every_occurrence():
    game = GameState("letter", ("Mira", "Eli"))

    result = game.submit_guess("T")

    assert result.status == "correct"
    assert result.guess == "t"
    assert game.masked_word == "__tt__"


def test_correct_word_guess_wins_for_current_player():
    game = GameState("cat", ("Mira", "Eli"))

    result = game.submit_guess("CAT")

    assert result.status == "won"
    assert result.player == "Mira"
    assert game.winner == "Mira"
    assert game.finished


def test_wrong_word_guess_costs_one_miss_and_rotates():
    game = GameState("cat", ("Mira", "Eli"))

    result = game.submit_guess("dog")

    assert result.status == "incorrect"
    assert game.miss_count == 1
    assert game.current_player == "Eli"


def test_invalid_guess_does_not_change_game_state():
    game = GameState("cat", ("Mira", "Eli"))
    game.submit_guess("a")

    duplicate = game.submit_guess("A")
    malformed = game.submit_guess("?")

    assert duplicate.status == "invalid"
    assert malformed.status == "invalid"
    assert game.masked_word == "_a_"
    assert game.current_player == "Eli"
    assert game.miss_count == 0


def test_eighth_miss_ends_game():
    game = GameState("abcdefgh", ("Solo",))

    for guess in "ijklmnop":
        result = game.submit_guess(guess)

    assert result.status == "lost"
    assert game.miss_count == 8
    assert game.finished
    assert game.winner is None
