"""Compatibility facade for action imports.

This module re-exports action classes so legacy imports like
`from class_action import *` keep working.

For easier navigation, action implementations are now split by domain:
- actions/season.py
- actions/points.py
- actions/resources.py
- actions/cards.py
- actions/locations.py

"""

from actions.base import *
from actions.cards import *
from actions.locations import *
from actions.points import *
from actions.resources import *
from actions.season import *
