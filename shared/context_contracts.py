from dataclasses import dataclass
from typing import Any, Protocol


class PlayCheckContext(Protocol):
    player: Any
    game_state: dict[str, Any]
    host_card: Any


@dataclass(frozen=True)
class SelectorPlayContext:
    player: Any
    game_state: dict[str, Any]
    host_card: Any
