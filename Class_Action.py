"""Compatibility facade for action and helper imports.

This module re-exports action classes and engine helper functions so existing
imports like `from Class_Action import *` keep working.

For easier navigation, action implementations are now split by domain:
- actions/season.py
- actions/points.py
- actions/resources.py
- actions/cards.py
- actions/locations.py

And game-flow/query helpers live in:
- engine/selectors.py
- engine/turn.py
"""

from actions import *
from engine.selectors import (
    get_critters_constructions_city,
    get_possible_cards,
    get_possible_locations,
    get_possible_moves,
)
from engine.turn import advance_current_player, finish_current_player
