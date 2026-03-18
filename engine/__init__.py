"""Engine helpers grouped by domain for easier discovery.

To add a new engine helper: write it in the appropriate domain file below
and include it in that file's `__all__` list.

Domain files:
- selectors.py: move/card/location selection and eligibility helpers
- turn.py     : turn progression and end-of-game helpers
"""

from engine.selectors import *
from engine.turn import *
