from Class_Action import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Class_Player import Player
    from Class_Meadow import Meadow
    from Class_Card import Card
    from Class_Location import Location


# ============================================
# ADVANCE CURRENT PLAYER AND FINISH CURRENT PLAYER
# ============================================

def advance_current_player(game_state):
    players = game_state["players"]
    current_player = game_state["current_player"]
    current_player_index = players.index(current_player)

    nr_not_finished = len([p for p in players if p.finished == False])
    if nr_not_finished != 1:
        # Find the next player that has not finished
        new_player_index = (current_player_index + 1) % len(players)
        while players[new_player_index].finished:
            new_player_index = (new_player_index + 1) % len(players)
        
        game_state["current_player"] = players[new_player_index]


def finish_current_player(game_state):

    # To do: set player.finished to True
    # To do: count each point type
    # To do: if it is the last player that finished, compare sum of points

    return


# ============================================
# GET POSSIBILITIES (cards to play, locations to place worker, moves to make)
# ============================================

def get_possible_cards(game_state):
    player: "Player" = game_state["current_player"]
    meadow = game_state["meadow"]
    possible_cards = []
    all_cards = player.hand + meadow.cards

    # Maximum city size
    if player.cards_get_open_spaces("city") == 0:
        return []
    
    else:
        for card in all_cards:
            # Player may only have one specific copy of any unique card
            if card.unique:
                if any(c.name == card.name for c in player.city):
                    continue


            # Check if player has sufficient resources for card requirements
            reqs = card.requirements
            has_resources = True
            for r, amt in reqs.items():
                if player.resources.get(r) < amt:
                    has_resources = False
                    break

            if has_resources:
                possible_cards.append(card)
                continue

            # Allow free play of critters when related to a played construction
            from Class_Card import Critter

            if isinstance(card, Critter):
                for constr in player.city:
                    if card.name in constr.relatedcritters:
                        if not constr.relatedoccupied:
                            possible_cards.append(card)
                            break

        # Remove duplicates
        possible_cards = list(dict.fromkeys(possible_cards))
        return possible_cards    


def get_possible_locations(game_state):

    # To do: for a destination card, it should be checked if the action
    # can be executed. For example, for the klooster, the player should have
    # enough resources to execute the action, otherwise it should not be a
    # possible location to place a worker.

    locations = game_state["locations"]
    location: "Location"
    possible_locations = []
    
    for location in locations:
        # Basic locations
        if location.type == "basic":
            if location.get_open_spaces() > 0:
                possible_locations.append(location)
        
        # Destination cards
        if location.type == "destination_card":

            # To do: check if card is in player's city
            # or if the card is open if in another player's city

            if location.get_open_spaces() > 0:
                possible_locations.append(location)            


    # To do: forest locations
    # To do: event
    # To do: haven
    # To do: journey

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
                card.action_on_reactivate.execute(game_state)    
    
    elif current_season == "spring":
        player.workers_add(1)
        action_draw_cards_from_meadow(2).execute(game_state)
    
    elif current_season == "summer":
        player.workers_add(2)
        for card in player.city:
            if card.color == "green":
                # On season change, execute action_on_reactivate
                if card.action_on_reactivate:
                    card.action_on_reactivate.execute(game_state)

    location: "Location"
    for location in game_state["locations"]:
        # Do not return workers placed on permanent locations (e.g., klooster)
        if (location.get_player_workers(player) > 0 and not 
                                getattr(location, "permanent_workers", False)):
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
        card = player.decide(game_state, "card_new", possible_cards)
        in_hand = card in player.hand
        in_meadow = card in meadow.cards

        loc = (
            player.decide(game_state, "card_hand_or_meadow", None)
            if in_hand and in_meadow
            else "hand" if in_hand
            else "meadow"
        )

        if loc == "hand":
            player.cards_remove([card], "hand")
        else:
            meadow.draw_cards([card], deck, discardpile)
                
        # To do: card can be played if a related card is played,
        #           no costs have to be paid, bút 
        #           the relatedoccupied should be set to True
        # To do: card can be played by discarding a card in the city,
        #           no or less costs have to paid

        # The player pays for the costs of the card
        card_costs = card.requirements
        for resource, amount in card_costs.items():
            player.resources_remove(resource, amount)
        
        # The card is added to the player's city and action_on_play is executed
        player.cards_add([card], "city")
        if card.action_on_play:
            card.action_on_play.execute(game_state)


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
