from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Class_Player import Player
    from Class_Deck import Deck
    from Class_DiscardPile import DiscardPile
    from Class_Meadow import Meadow
    from Class_Card import Card
    from Class_Location import Location
    from Class_Strategy import Strategy


# Function to retrieve all possible cards a player can play from hand and meadow
def get_possible_cards(game_state):
    player = game_state["current_player"]
    meadow = game_state["meadow"]
    possible_cards = []
    for card in player.hand:
        for r in card.requirements:
            if player.resources.get(r) < card.requirements.get(r):
                break
        else:
            possible_cards.append(card)
    for card in meadow.cards:
        for r in card.requirements:
            if player.resources.get(r) < card.requirements.get(r):
                break
        else:
            possible_cards.append(card)
    return possible_cards            


# Get possible locations to place worker
def get_possible_locations(game_state):    
    locations = game_state["locations"]
    location: "Location"
    possible_locations = []
    
    for location in locations:
        # Basic locations
        if location.type == "basic":
            if location.get_open_spaces() > 0:
                possible_locations.append(location)


    # To add: forest locations
    # To add: event
    # To add: haven
    # To add: journey 
    # To add: destination cards

    return possible_locations


# ============================================
# Get possible moves
# ============================================

    # No only check possible locations, but also can I place a worker? / available workers


"""
A player can make three main moves. These moves are:
"""

# ============================================
# Place worker
# ============================================

def place_worker(game_state):
    player: "Player" = game_state["current_player"]
    preferred_location = player.decide(game_state, "location", get_possible_locations(game_state))
    preferred_location.add_worker(player)
    player.workers_remove(1)
    return



# ============================================
# Play card
# ============================================

# When playing a card, the following things should be checked
    # Are there any blue cards in the city that are executed?
        # Historicus, after playing critter or construction
        # Winkelier, after playing critter
        # Gerechtsgebouw, after playing construction

    # Are there any blue cards in the city that are used?
        # Rechter, when playing another critter or construction
        # Herbergier, when playing another critter
        # Kerker, when playing another critter or construction


# ============================================
# Advance season
# ============================================


    # Check the current season
    # Check the number of workers on hand
    # Execute actions from cards
    # Execute actions from season (spring: add 1 worker + execute green, summer: add 1 worker + draw 2 cards from meadow, autumn: add 2 workers + execture green)
    # Bring back workers
