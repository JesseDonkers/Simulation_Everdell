from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Class_Player import Player
    from Class_Deck import Deck
    from Class_DiscardPile import DiscardPile
    from Class_Meadow import Meadow
    from Class_Card import Card
    from Class_Location import Location


# Function to retrieve all possible cards a player can play from hand and meadow
def get_possible_cards(game_state):
    player = game_state['current_player']
    meadow = game_state['meadow']
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
    locations = game_state['locations']
    location: 'Location'
    possible_locations = []
    
    # Basic locations
    for location in locations:
        if location.check_open_spaces() > 0:
            possible_locations.append(location)

    # To add: forest locations
    # To add: basic event
    # To add: special event
    # To add: haven
    # To add: journey 
    # To add: destination cards

    return possible_locations


# A player can perform three main actions, these actions should be modeled
# The three main actions are:
    # Place worker (choose location)
    # Play card (Choose card)
    # Prepare for season

# But for these actions the following functions are required
    # A function should be created to check which actions are possible
    # A function should be created to choose which action to execute


def prepare_for_season(deck, discardpile, meadow, player):
    # Check the current season
    # Check the number of workers on hand
    # Execute actions from cards
    # Execute actions from season (spring: add 1 worker + execute green, summer: add 1 worker + draw 2 cards from meadow, autumn: add 2 workers + execture green)
    # Bring back workers
    return deck, discardpile, meadow, player