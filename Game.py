from Class_Deck import *
from Class_DiscardPile import *
from Class_Meadow import *
from Class_Player import *
from Class_Card import *
from Class_Location import *
from Class_Action import *


# Initialize game state
game_state = {
    'deck': [],               # List of cards to draw from
    'discardpile': [],        # Cards that have been discarded
    'meadow': [],             # The 8 available cards in the meadow
    'locations': [],          # All available locations
    'players': [],            # All players in the game
    'current_player': None,   # Whose turn it is
}


"""
Start game
"""
# Initialze cards

# Initialize deck
# Shuffle deck

# Initialize discard pile

# Initialize meadow
# Place cards in meadow

# Initialize players
# Players draw cards
# Players take workers

# Shuffle special events
# Draw 4 special events
# Shuffle forest cards
# Place 3 or 4 forecst cards depending on number of players

"""
End game
"""
# No more possible actions or every player has passed
# Winner is the one with the most points, when tie, most resources

