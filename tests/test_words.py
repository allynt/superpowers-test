import words


def test_choose_word_returns_a_curated_word(monkeypatch):
    def choose_amber(entries):
        assert "amber" in entries
        return "amber"

    monkeypatch.setattr(words.random, "choice", choose_amber)

    assert words.choose_word() == "amber"
