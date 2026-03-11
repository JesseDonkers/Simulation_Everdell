"""Action modules grouped by domain for easier discovery.

To add a new action: write the class in the appropriate domain file below.
It will automatically be available everywhere via `from Class_Action import *`.

Domain files:
- base.py    : Action base class, CompositeAction
- season.py  : season progression actions
- points.py  : point/token/prosperity actions
- resources.py: resource and discard-to-gain actions
- cards.py   : card draw/play/refresh actions
- locations.py: worker placement and destination location actions
"""

from actions.base import *
from actions.cards import *
from actions.locations import *
from actions.points import *
from actions.resources import *
from actions.season import *
