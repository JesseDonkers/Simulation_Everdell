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
    pay_requirements: dict[str, int] | None = None
    source_card: Any = None
    consumed_cards: tuple[Any, ...] = ()


@dataclass(frozen=True)
class PlayCardOption:
    card: "Card"
    methods: list[PlayMethod]


def _has_resources(resources, requirements):
    for resource, amount in requirements.items():
        if resources.get(resource, 0) < amount:
            return False
    return True


def _dedupe_play_methods(methods):
    unique_methods = []
    seen = set()

    for method in methods:
        pay_req_tuple = (
            tuple(sorted(method.pay_requirements.items()))
            if method.pay_requirements else None
        )
        key = (
            method.method,
            pay_req_tuple,
            id(method.source_card) if method.source_card else None,
            tuple(id(card) for card in method.consumed_cards),
        )
        if key not in seen:
            seen.add(key)
            unique_methods.append(method)

    return unique_methods


def _iter_discounted_requirements(requirements, discount):
    twig = requirements.get("twig", 0)
    resin = requirements.get("resin", 0)
    pebble = requirements.get("pebble", 0)
    berry = requirements.get("berry", 0)

    max_discount = min(discount, twig + resin + pebble + berry)
    unique_costs = []
    seen = set()

    for twig_reduce in range(min(twig, max_discount) + 1):
        rem_after_twig = max_discount - twig_reduce

        for resin_reduce in range(min(resin, rem_after_twig) + 1):
            rem_after_resin = rem_after_twig - resin_reduce

            for pebble_reduce in range(min(pebble, rem_after_resin) + 1):
                rem_after_pebble = rem_after_resin - pebble_reduce

                for berry_reduce in range(min(berry, rem_after_pebble) + 1):
                    # Partial discount is allowed, so not all discount
                    # must be used.
                    cost = {
                        "twig": twig - twig_reduce,
                        "resin": resin - resin_reduce,
                        "pebble": pebble - pebble_reduce,
                        "berry": berry - berry_reduce,
                    }

                    key = (
                        cost["twig"],
                        cost["resin"],
                        cost["pebble"],
                        cost["berry"],
                    )
                    if key not in seen:
                        seen.add(key)
                        unique_costs.append(cost)

    return unique_costs


def _get_kerker_methods(player, card):
    from class_card import Construction, Critter

    if not isinstance(card, (Construction, Critter)):
        return []

    kerker = next(
        (city_card for city_card in player.city
         if city_card.name == "Kerker"),
        None,
    )
    if kerker is None:
        return []

    has_boswachter = any(
        city_card.name == "Boswachter" for city_card in player.city
    )
    capacity = 2 if has_boswachter else 1
    if len(kerker.stored_cards) >= capacity:
        return []

    prisoners = [
        city_card for city_card in player.city
        if isinstance(city_card, Critter)
    ]
    methods = []

    for prisoner in prisoners:
        for reduced_cost in _iter_discounted_requirements(
            card.requirements, discount=3
        ):
            if _has_resources(player.resources, reduced_cost):
                methods.append(
                    PlayMethod(
                        method="kerker_discount",
                        requires_city_discard=False,
                        city_discard_optional=False,
                        pay_requirements=reduced_cost,
                        source_card=kerker,
                        consumed_cards=(prisoner,),
                    )
                )

    return methods


def get_possible_card_plays(
    game_state,
    max_points=99,
    pay=True,
    allow_city_discard_then_pay=False,
):
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
                    pay_requirements=None,
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
                        pay_requirements=dict(card.requirements),
                    )
                )

            # Free play of critters when related to a played construction
            if isinstance(card, Critter):
                constructions = [
                    c for c in player.city if isinstance(c, Construction)
                ]
                for constr in constructions:
                    if (
                        card.name in constr.relatedcritters
                        and not constr.relatedoccupied
                    ):
                        methods.append(
                            PlayMethod(
                                method="related_free",
                                requires_city_discard=False,
                                city_discard_optional=False,
                                pay_requirements=None,
                                source_card=constr,
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

                    if _has_resources(
                        resources_after_discard, card.requirements
                    ):
                        methods.append(
                            PlayMethod(
                                method="city_discard_then_pay",
                                requires_city_discard=True,
                                city_discard_optional=_has_resources(
                                    player.resources,
                                    card.requirements,
                                ),
                                pay_requirements=dict(card.requirements),
                                consumed_cards=(city_card,),
                            )
                        )

            methods.extend(_get_kerker_methods(player, card))

        final_methods = _dedupe_play_methods(methods)

        if len(final_methods) > 0:
            possible_card_plays.append(
                PlayCardOption(card=card, methods=final_methods)
            )

    return possible_card_plays


def get_possible_cards(
    game_state,
    max_points=99,
    pay=True,
    allow_city_discard_then_pay=False,
):
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
