# Hangman

One-round terminal Hangman for solo and multiplayer play, built with Python, Click, and Rich.

> [!NOTE]
> This project is a personal learning exercise for using [Superpowers](https://github.com/obra/superpowers).

[![Python 3.13+](https://img.shields.io/badge/Python-3.13%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Tests](https://github.com/allynt/superpowers-test/actions/workflows/tests.yml/badge.svg)](https://github.com/allynt/superpowers-test/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Built with Click and Rich](https://img.shields.io/badge/Built%20with-Click%20%2B%20Rich-orange)

## Play

Install the project dependencies:

```bash
uv sync
```

Start a single-player game:

```bash
uv run python src/main.py --player Mira
```

Start a multiplayer game by repeating `--player` for each player:

```bash
uv run python src/main.py --player Mira --player Eli
```

## Addendum

initial copilot credit usage: 126.9
