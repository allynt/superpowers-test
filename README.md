PAT: [REDACTED]

initial copilot credit usage: 126.9

## Hangman

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
