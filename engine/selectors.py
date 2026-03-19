from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from class_location import Location

__all__ = [
    "get_critters_constructions_city",
    "get_possible_cards",
    "get_possible_locations",
    "get_possible_moves",
]


def get_possible_cards(game_state, max_points, pay):
    player = game_state["current_player"]
    meadow = game_state["meadow"]
    all_cards = player.hand + meadow.cards
    possible_cards = []

    # Maximum city size
    if player.cards_get_open_spaces("city") == 0:
        return possible_cards

    for card in all_cards:
        # Cards are only allowed when not exceeding the max points
        if card.points > max_points:
            continue

        # Player may only have one specific copy of any unique card
        if card.unique and any(c.name == card.name for c in player.city):
            continue

        # Check if player has enough resources for card requirements
        if pay:
            reqs = card.requirements
            has_resources = True
            for r, amt in reqs.items():
                if player.resources.get(r) < amt:
                    has_resources = False
                    break

            if has_resources:
                possible_cards.append(card)
                continue
        else:
            possible_cards.append(card)

        # Free play of critters when related to a played construction
        if max_points == 99:
            from class_card import Construction, Critter

            constructions = [
                c for c in player.city if isinstance(c, Construction)
            ]

            if isinstance(card, Critter):
                for constr in constructions:
                    if (card.name in constr.relatedcritters 
                                            and not constr.relatedoccupied):
                        possible_cards.append(card)
                        break

    # Remove duplicates while preserving order
    possible_cards = list(dict.fromkeys(possible_cards))
    return possible_cards


def get_possible_locations(game_state):
    # To do: for a destination card, it should be checked if the action
    # can be executed.
    # 
    # For example, for the klooster, the player should have
    # enough resources to execute the action, otherwise it should not be a
    # possible location to place a worker.

    player = game_state["current_player"]
    locations = game_state["locations"]
    location: "Location"
    possible_locations = []

    for location in locations:
        # Basic locations
        if location.type == "basic" and location.get_open_spaces() > 0:
            possible_locations.append(location)

        # Destination cards
        if location.type == "destination_card":
            owner = getattr(location, "owner", None)
            in_own_city = owner == player
            accessible_open = owner is not None and (
                                            owner != player and location.open)

            if location.get_open_spaces() > 0 and (
                                            in_own_city or accessible_open):
                possible_locations.append(location)

        # Haven locations
        if location.type == "haven" and location.get_open_spaces() > 0:
            possible_locations.append(location)

        # Journey locations (autumn only)
        if location.type == "journey":
            in_autumn = player.season == "autumn"
            has_space = location.get_open_spaces() > 0
            can_discard_required_cards = len(player.hand) >= location.points

            if in_autumn and has_space and can_discard_required_cards:
                possible_locations.append(location)

    # To do: forest locations
    # To do: event

    return possible_locations


def get_possible_moves(game_state):
    possible_moves = []
    possible_cards = get_possible_cards(game_state, 99, True)
    possible_locations = get_possible_locations(game_state)
    workers = game_state["current_player"].workers

    if len(possible_cards) > 0:
        possible_moves.append("play_card")
    if len(possible_locations) > 0 and workers > 0:
        possible_moves.append("place_worker")
    if game_state["current_player"].season != "autumn" and workers == 0:
        possible_moves.append("advance_season")
    return possible_moves


def get_critters_constructions_city(game_state, critter_and_construction):
    from class_card import Construction, Critter

    player = game_state["current_player"]
    critter = critter_and_construction[0]
    construction = critter_and_construction[1]

    options = []
    if critter and not construction:
        options = [c for c in player.city if isinstance(c, Critter)]
    elif construction and not critter:
        options = [c for c in player.city if isinstance(c, Construction)]
    else:
        # If neither flag is set or both are set, allow any card in city
        options = list(player.city)

    return options
