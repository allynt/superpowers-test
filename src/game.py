from dataclasses import dataclass, field
from typing import Literal, TypeAlias


MAX_MISSES = 8
GuessStatus: TypeAlias = Literal["correct", "incorrect", "invalid", "won", "lost"]


@dataclass(frozen=True)
class GuessResult:
    status: GuessStatus
    player: str
    guess: str


@dataclass
class GameState:
    word: str
    players: tuple[str, ...]
    miss_count: int = field(default=0, init=False)
    finished: bool = field(default=False, init=False)
    winner: str | None = field(default=None, init=False)
    _guessed_letters: set[str] = field(default_factory=set, init=False, repr=False)
    _guesses: set[str] = field(default_factory=set, init=False, repr=False)
    _turn_index: int = field(default=0, init=False, repr=False)

    def __post_init__(self) -> None:
        self.word = self.word.strip().lower()
        self.players = tuple(self.players)
        if not self.word or not self.word.isalpha():
            raise ValueError("word must contain letters")
        if not self.players or any(not player.strip() for player in self.players):
            raise ValueError("at least one named player is required")

    @property
    def current_player(self) -> str:
        return self.players[self._turn_index]

    @property
    def masked_word(self) -> str:
        return "".join(letter if letter in self._guessed_letters else "_" for letter in self.word)

    def submit_guess(self, guess: str) -> GuessResult:
        player = self.current_player
        normalized = guess.strip().lower() if isinstance(guess, str) else ""

        if self.finished or not normalized.isalpha() or normalized in self._guesses:
            return GuessResult("invalid", player, normalized)

        self._guesses.add(normalized)
        if len(normalized) == 1:
            if normalized in self.word:
                self._guessed_letters.add(normalized)
                if all(letter in self._guessed_letters for letter in self.word):
                    self.finished = True
                    self.winner = player
                    return GuessResult("won", player, normalized)
                self._advance_turn()
                return GuessResult("correct", player, normalized)

        elif normalized == self.word:
            self._guessed_letters.update(self.word)
            self.finished = True
            self.winner = player
            return GuessResult("won", player, normalized)

        self.miss_count += 1
        if self.miss_count == MAX_MISSES:
            self.finished = True
            return GuessResult("lost", player, normalized)

        self._advance_turn()
        return GuessResult("incorrect", player, normalized)

    def _advance_turn(self) -> None:
        self._turn_index = (self._turn_index + 1) % len(self.players)
