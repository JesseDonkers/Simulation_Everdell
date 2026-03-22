from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from class_card import Card
    from class_location import Location

__all__ = [
    "PlayCardOption",
    "PlayMethod",
    "get_critters_constructions_city",
    "get_possible_card_plays",
    "get_possible_cards",
    "get_possible_locations",
    "get_possible_moves",
]


@dataclass(frozen=True)
class PlayMethod:
    method: str
    requires_city_discard: bool
    city_discard_optional: bool
    related_construction: Any = None
    city_discard_card: Any = None


@dataclass(frozen=True)
class PlayCardOption:
    card: "Card"
    methods: list[PlayMethod]


def _has_resources(resources, requirements):
    for resource, amount in requirements.items():
        if resources.get(resource, 0) < amount:
            return False
    return True


def get_possible_card_plays(game_state, max_points=99, pay=True, allow_city_discard_then_pay=False):
    player = game_state["current_player"]
    meadow = game_state["meadow"]
    all_cards = player.hand + meadow.cards
    possible_card_plays = []

    # Maximum city size
    if player.cards_get_open_spaces("city") == 0:
        return possible_card_plays

    from class_card import Construction, Critter

    for card in all_cards:
        # Cards are only allowed when not exceeding the max points
        if card.points > max_points:
            continue

        # Player may only have one specific copy of any unique card
        if card.unique and any(c.name == card.name for c in player.city):
            continue

        methods = []

        # Play actions that explicitly do not pay costs
        if not pay:
            methods.append(
                PlayMethod(
                    method="free_no_pay",
                    requires_city_discard=False,
                    city_discard_optional=False,
                )
            )

        # Resource-paid and alternative methods
        if pay:
            if _has_resources(player.resources, card.requirements):
                methods.append(
                    PlayMethod(
                        method="pay_resources",
                        requires_city_discard=False,
                        city_discard_optional=True,
                    )
                )

            # Free play of critters when related to a played construction
            if isinstance(card, Critter):
                constructions = [
                    c for c in player.city if isinstance(c, Construction)
                ]
                for constr in constructions:
                    if card.name in constr.relatedcritters and not constr.relatedoccupied:
                        methods.append(
                            PlayMethod(
                                method="related_free",
                                requires_city_discard=False,
                                city_discard_optional=False,
                                related_construction=constr,
                            )
                        )

            # Non-standard method: discard a city card to gain resources
            # before paying. This is only available when explicitly enabled.
            if allow_city_discard_then_pay:
                for city_card in player.city:
                    resources_after_discard = dict(player.resources)
                    for resource, amount in city_card.requirements.items():
                        resources_after_discard[resource] = (
                            resources_after_discard.get(resource, 0) + amount
                        )

                    if _has_resources(resources_after_discard, card.requirements):
                        methods.append(
                            PlayMethod(
                                method="city_discard_then_pay",
                                requires_city_discard=True,
                                city_discard_optional=_has_resources(
                                    player.resources,
                                    card.requirements,
                                ),
                                city_discard_card=city_card,
                            )
                        )

        # Remove duplicate methods while preserving order.
        unique_methods = []
        seen = set()
        for method in methods:
            key = (
                method.method,
                id(method.related_construction) if method.related_construction else None,
                id(method.city_discard_card) if method.city_discard_card else None,
            )
            if key not in seen:
                seen.add(key)
                unique_methods.append(method)

        if len(unique_methods) > 0:
            possible_card_plays.append(PlayCardOption(card=card, methods=unique_methods))

    return possible_card_plays


def get_possible_cards(game_state, max_points=99, pay=True, allow_city_discard_then_pay=False):
    possible_card_plays = get_possible_card_plays(
        game_state,
        max_points,
        pay,
        allow_city_discard_then_pay=allow_city_discard_then_pay,
    )
    possible_cards = [entry.card for entry in possible_card_plays]

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
