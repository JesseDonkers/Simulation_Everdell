from dataclasses import dataclass
from typing import Any, Protocol

from shared.game_state import GameState


class PlayCheckContext(Protocol):
    player: Any
    game_state: GameState
    host_card: Any


@dataclass(frozen=True)
class SelectorPlayContext:
    player: Any
    game_state: GameState
    host_card: Any
