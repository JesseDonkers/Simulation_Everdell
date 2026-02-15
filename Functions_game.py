from Class_Action import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Class_Player import Player
    from Class_Meadow import Meadow
    from Class_Card import Card
    from Class_Location import Location


# ============================================
# GET POSSIBILITIES (cards to play, locations to place worker, moves to make)
# ============================================

def get_possible_cards(game_state):
    player = game_state["current_player"]
    meadow = game_state["meadow"]
    possible_cards = []
    all_cards = player.hand + meadow.cards

    for card in all_cards:
        for r in card.requirements:
            if player.resources.get(r) < card.requirements.get(r):
                break
        else:
            possible_cards.append(card)

        # To do: check for related critters / constructions
   
    return possible_cards            


def get_possible_locations(game_state):    
    locations = game_state["locations"]
    location: "Location"
    possible_locations = []
    
    for location in locations:
        # Basic locations
        if location.type == "basic":
            if location.get_open_spaces() > 0:
                possible_locations.append(location)


    # To do: forest locations
    # To do: event
    # To do: haven
    # To do: journey 
    # To do: destination cards

    return possible_locations


def get_possible_moves(game_state):
    possible_moves = []
    possible_cards = get_possible_cards(game_state)
    possible_locations = get_possible_locations(game_state)
    workers = game_state["current_player"].workers

    if len(possible_cards) > 0:
        possible_moves.append("play_card")
    if len(possible_locations) > 0 and workers > 0:
        possible_moves.append("place_worker")
    if game_state["current_player"].season != "autumn" and workers == 0:
        possible_moves.append("advance_season")
    return possible_moves


# ============================================
# THREE MAIN MOVES (place worker, advance season, play card)
# ============================================

def place_worker(game_state):
    player: "Player" = game_state["current_player"]
    preferred_location: "Location"
    possib_loc = get_possible_locations(game_state)

    if len(possib_loc) == 0:
        raise ValueError("No possible locations to place worker")
    else:
        preferred_location = player.decide(game_state, "location", possib_loc)
        preferred_location.add_worker(player)
        player.workers_remove(1)
        preferred_location.action.execute(game_state)
    return


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


def play_card(game_state):
    player: "Player" = game_state["current_player"]
    meadow: "Meadow" = game_state["meadow"]
    deck = game_state["deck"]
    discardpile = game_state["discardpile"]
    
    possible_cards = get_possible_cards(game_state)
    if len(possible_cards) == 0:
        raise ValueError("No possible cards to play")
    
    else:
        preferred_card = player.decide(game_state, "card", possible_cards)

        # To do: what if a card is in a player's hand ánd in the meadow?

        if preferred_card in player.hand:
            player.cards_remove([preferred_card], "hand")
        else:
            meadow.draw_cards([preferred_card], deck, discardpile)
                
        # To do: card can be played if a related card is played,
        #           no costs have to be paid
        # To do: card can be played by discarding a card in the city,
        #              no or less costs have to paid

        # The player pays for the costs of the card
        card_costs = preferred_card.requirements
        for resource, amount in card_costs.items():
            player.resources_remove(resource, amount)
        
        # The card is added to the player's city and its action is executed
        player.cards_add([preferred_card], "city")
        preferred_card.action.execute(game_state)




    # To do:
    # When playing a card, the following things should be checked
        # Are there any blue cards in the city that are executed?
            # Historicus, after playing critter or construction
            # Winkelier, after playing critter
            # Gerechtsgebouw, after playing construction

        # Are there any blue cards in the city that are used?
            # Rechter, when playing another critter or construction
            # Herbergier, when playing another critter
            # Kerker, when playing another critter or construction

    return
