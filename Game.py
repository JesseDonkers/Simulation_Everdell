from Class_Deck import Deck
from Class_DiscardPile import DiscardPile
from Class_Meadow import Meadow
from Class_Player import Player
from Game_locations import locations
from Game_cards import cards

# ============================================
# VARIABLES
# ============================================

nrPlayers = 2  # Number of players in the game (2-4)


# ============================================
# SET UP GAME
# ============================================

deck = Deck()
deck.add_to_deck(cards)
deck.shuffle_deck()

discardpile = DiscardPile()
meadow = Meadow()
meadow.add_to_meadow(8, deck, discardpile)

players = []
for _ in range(nrPlayers):
    player = Player()
    # Players draw cards
    # Players take workers
    players.append(player)


"""
To do:
 - Shuffle special events
 - Draw 4 special events
 - Shuffle forest cards
 - Place 3 or 4 forecst cards depending on number of players
"""


game_state = {
    'deck': deck,                 # List of cards to draw from
    'discardpile': discardpile,          # Cards that have been discarded
    'meadow': meadow,               # The 8 available cards in the meadow
    'locations': locations,     # All locations
    'players': players,              # All players in the game
    'current_player': None,     # Tracker for whose turn it is
}


"""
End game
"""
# No more possible actions or every player has passed
# Winner is the one with the most points, when tie, most resources

