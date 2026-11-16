import random


WORDS: tuple[str, ...] = (
    "amber",
    "apple",
    "beach",
    "candle",
    "dragon",
    "forest",
    "guitar",
    "island",
    "jacket",
    "kitten",
    "lemon",
    "mountain",
    "napkin",
    "orange",
    "pencil",
    "rocket",
    "silver",
    "tunnel",
    "velvet",
    "window",
    "yellow",
)
"""Curated words that can be used as Hangman answers."""


def choose_word() -> str:
    """Return a randomly selected word from the curated list."""
    return random.choice(WORDS)
