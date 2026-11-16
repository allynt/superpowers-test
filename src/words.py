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


def choose_word() -> str:
    return random.choice(WORDS)
