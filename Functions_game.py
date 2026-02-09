from Class_Action import *
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


# Function to obtain a list of the possible moves a player can make
def get_possible_moves(game_state):
    possible_moves = []
    possible_cards = get_possible_cards(game_state)
    possible_locations = get_possible_locations(game_state)
    if len(possible_cards) > 0:
        possible_moves.append("play_card")
    if len(possible_locations) > 0 and game_state["current_player"].workers > 0:
        possible_moves.append("place_worker")
    if game_state["current_player"].season != "autumn" and game_state["current_player"].workers == 0:
        possible_moves.append("advance_season")
    return possible_moves


# One of the three moves a player can make is placing a worker
def place_worker(game_state):
    player: "Player" = game_state["current_player"]
    preferred_location = player.decide(game_state, "location", get_possible_locations(game_state))
    preferred_location.add_worker(player)
    player.workers_remove(1)
    return


# The second move a player can make is advancing to the next season
def advance_season(game_state):
    player: "Player" = game_state["current_player"]
    seasons = ["winter", "spring", "summer", "autumn"]
    current_season = player.season
    current_index = seasons.index(player.season)

    if current_season == "winter":
        player.workers_add(1)
        card: "Card"
        for card in player.city:
            if card.color == "green":
                card.action.execute(game_state)    
    
    elif current_season == "spring":
        player.workers_add(1)
        action_draw_cards_from_meadow(2).execute(game_state)
    
    elif current_season == "summer":
        player.workers_add(2)
        for card in player.city:
            if card.color == "green":
                card.action.execute(game_state)

    location: "Location"
    for location in game_state["locations"]:
        if location.get_player_workers(player) > 0:
            location.remove_worker(player)
            player.workers_add(1)
    
    player.season = seasons[(current_index + 1)]
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




