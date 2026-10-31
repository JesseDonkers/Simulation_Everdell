from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from class_deck import Deck
    from class_discard_pile import DiscardPile
    from class_location import Location
    from class_meadow import Meadow
    from class_player import Player


@dataclass
class GameState:
    deck: Deck
    discardpile: DiscardPile
    meadow: Meadow
    locations: list[Location]
    players: list[Player]
    current_player: Player