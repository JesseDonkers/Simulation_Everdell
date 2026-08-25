from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from shared.context_contracts import SelectorPlayContext
from shared.play_plan import EXTERNAL_PLAY_ABILITY, build_play_plan

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
    "get_possible_meadow_card_plays_with_discount",
    "get_possible_moves",
    "get_valid_rechter_swaps",
]


@dataclass(frozen=True)
class PlayMethod:
    method: str
    requires_city_discard: bool
    city_discard_optional: bool
    pay_requirements: dict[str, int] | None = None
    source_card: Any = None
    consumed_cards: tuple[Any, ...] = ()
    creates_city_space_before_place: bool = False
    play_tags: tuple[str, ...] = ()
    play_conflicts: tuple[str, ...] = ()


@dataclass(frozen=True)
class PlayCardOption:
    card: "Card"
    methods: list[PlayMethod]


def _has_resources(resources, requirements):
    for resource, amount in requirements.items():
        if resources.get(resource, 0) < amount:
            return False
    return True


def _location_requirement_met(player, loc, requirement, game_state):
    kind = requirement.get("kind")

    if kind == "min_color_cards":
        color = requirement.get("color")
        count = requirement.get("count", 0)
        city_count = len([card for card in player.city if card.color == color])
        return city_count >= count

    if kind == "required_cards_in_city":
        required_cards = requirement.get("cards", [])
        city_names = {card.name for card in player.city}
        return all(card_name in city_names for card_name in required_cards)

    from class_card import Critter, Construction

    if kind == "construction_or_critter_in_city":
        required_type = requirement.get("construction_or_critter")
        return (
            any(isinstance(card, Critter) for card in player.city)
            if required_type == "critter"
            else any(isinstance(card, Construction) for card in player.city)
        )

    if kind == "has_resource_type":
        resource = requirement.get("resource")
        amount = requirement.get("amount", 1)
        return player.resources.get(resource, 0) >= amount

    if kind == "has_any_resource":
        return sum(player.resources.values()) >= 1

    if kind == "has_hand_cards":
        amount = requirement.get("amount", 1)
        return len(player.hand) >= amount

    if kind == "other_player_has_hand_space":
        amount = requirement.get("amount", 1)
        return any(
            p != player and not p.finished and p.cards_get_open_spaces("hand") >= amount
            for p in game_state["players"]
        )

    if kind == "has_placed_worker":
        return any(
            loc.get_player_workers(player) > 0
            and not getattr(loc, "permanent_workers", False)
            for loc in game_state["locations"]
        )

    if kind == "has_city_cards":
        amount = requirement.get("amount", 1)
        return len(player.city) >= amount

    if kind == "has_city_space":
        return player.cards_get_open_spaces("city") > 0

    if kind == "other_player_has_city_space":
        return any(
            p != player and not p.finished and p.cards_get_open_spaces("city") > 0
            for p in game_state["players"]
        )

    if kind == "has_playable_meadow_card":
        discount = requirement.get("discount", 3)
        return (
            len(get_possible_meadow_card_plays_with_discount(game_state, discount)) > 0
        )

    if kind == "has_playable_card_with_max_points":
        max_points = requirement.get("max_points", 99)
        return (
            len(
                get_possible_card_plays(
                    game_state,
                    max_points=max_points,
                    pay=True,
                )
            )
            > 0
        )

    return False


def _requirements_met(player, loc, game_state):
    requirements = getattr(loc, "requirements", None)

    if requirements is None:
        return True

    if isinstance(requirements, (list, tuple)):
        return all(
            _location_requirement_met(player, loc, requirement, game_state)
            for requirement in requirements
        )

    return _location_requirement_met(player, loc, requirements, game_state)


def _dedupe_play_methods(methods):
    unique_methods = []
    seen = set()

    for method in methods:
        pay_req_tuple = (
            tuple(sorted(method.pay_requirements.items()))
            if method.pay_requirements
            else None
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
    """
    Generate all distinct discounted cost distributions for a card, given a
    fixed discount amount.

    The discount is always applied at its maximum useful value — capped by
    the card's total cost (min(discount, total_cost)) — never partially.
    There is no strategic reason to use less than the full discount, since
    the discount itself costs the player nothing. The only real choice is
    *which* resource types absorb the reduction.
    """
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
                    total_reduced = (
                        twig_reduce + resin_reduce + pebble_reduce + berry_reduce
                    )
                    if total_reduced != max_discount:
                        continue

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


def get_valid_rechter_swaps(player, card):
    """
    All (remove_type, add_type) pairs where swapping 1 unit of remove_type
    for 1 unit of add_type in the card's cost still leaves it payable.
    """
    resource_types = ("twig", "resin", "pebble", "berry")
    valid_swaps = []

    for remove_type in resource_types:
        if card.costs.get(remove_type, 0) <= 0:
            continue

        for add_type in resource_types:
            if add_type == remove_type:
                continue

            reduced_cost = dict(card.costs)
            reduced_cost[remove_type] -= 1
            reduced_cost[add_type] = reduced_cost.get(add_type, 0) + 1

            if _has_resources(player.resources, reduced_cost):
                valid_swaps.append((remove_type, add_type))

    return valid_swaps


def _get_rechter_methods(player, card):
    rechter = next(
        (city_card for city_card in player.city if city_card.name == "Rechter"),
        None,
    )
    if rechter is None:
        return []

    # A single method regardless of how many swaps are possible, so it isn't
    # over-represented versus other methods when a strategy picks randomly.
    if len(get_valid_rechter_swaps(player, card)) == 0:
        return []

    return [
        PlayMethod(
            method="rechter_substitution",
            requires_city_discard=False,
            city_discard_optional=False,
            pay_requirements=None,
            source_card=rechter,
            play_tags=(EXTERNAL_PLAY_ABILITY,),
            play_conflicts=(EXTERNAL_PLAY_ABILITY,),
        )
    ]


def _get_kraan_methods(player, card):
    from class_card import Construction

    if not isinstance(card, Construction):
        return []

    kraan = next(
        (city_card for city_card in player.city if city_card.name == "Kraan"),
        None,
    )
    if kraan is None:
        return []

    methods = []
    for reduced_cost in _iter_discounted_requirements(card.costs, discount=3):
        if _has_resources(player.resources, reduced_cost):
            methods.append(
                PlayMethod(
                    method="kraan_discount",
                    requires_city_discard=False,
                    city_discard_optional=False,
                    pay_requirements=reduced_cost,
                    source_card=kraan,
                    consumed_cards=(kraan,),
                    creates_city_space_before_place=True,
                    play_tags=(EXTERNAL_PLAY_ABILITY,),
                    play_conflicts=(EXTERNAL_PLAY_ABILITY,),
                )
            )

    return methods


def _get_herbergier_methods(player, card):
    from class_card import Critter

    if not isinstance(card, Critter):
        return []

    herbergier = next(
        (city_card for city_card in player.city if city_card.name == "Herbergier"),
        None,
    )
    if herbergier is None:
        return []

    discount = min(3, card.costs.get("berry", 0))
    reduced_cost = dict(card.costs)
    reduced_cost["berry"] -= discount

    if not _has_resources(player.resources, reduced_cost):
        return []

    return [
        PlayMethod(
            method="herbergier_discount",
            requires_city_discard=False,
            city_discard_optional=False,
            pay_requirements=reduced_cost,
            source_card=herbergier,
            consumed_cards=(herbergier,),
            creates_city_space_before_place=True,
            play_tags=(EXTERNAL_PLAY_ABILITY,),
            play_conflicts=(EXTERNAL_PLAY_ABILITY,),
        )
    ]


def _get_kerker_methods(player, card):
    from class_card import Construction, Critter

    if not isinstance(card, (Construction, Critter)):
        return []

    kerker = next(
        (city_card for city_card in player.city if city_card.name == "Kerker"),
        None,
    )
    if kerker is None:
        return []

    has_boswachter = any(city_card.name == "Boswachter" for city_card in player.city)
    capacity = 2 if has_boswachter else 1
    if len(kerker.card_storage["cards"]) >= capacity:
        return []

    prisoners = [
        city_card for city_card in player.city if isinstance(city_card, Critter)
    ]
    methods = []

    for prisoner in prisoners:
        for reduced_cost in _iter_discounted_requirements(card.costs, discount=3):
            if _has_resources(player.resources, reduced_cost):
                methods.append(
                    PlayMethod(
                        method="kerker_discount",
                        requires_city_discard=False,
                        city_discard_optional=False,
                        pay_requirements=reduced_cost,
                        source_card=kerker,
                        consumed_cards=(prisoner,),
                        creates_city_space_before_place=True,
                        play_tags=(EXTERNAL_PLAY_ABILITY,),
                        play_conflicts=(EXTERNAL_PLAY_ABILITY,),
                    )
                )

    return methods


def _card_can_create_space_before_place(player, card, game_state):
    effect = getattr(card, "action_on_play", None)
    if effect is None:
        return False

    child_actions = getattr(effect, "actions", None)
    actions = child_actions if child_actions is not None else [effect]

    for action in actions:
        if getattr(action, "play_timing", "post_place") != "pre_place":
            continue
        if not getattr(action, "creates_city_space_before_place", False):
            continue

        if action.can_create_city_space_before_place(
            SelectorPlayContext(
                player=player,
                game_state=game_state,
                host_card=card,
            )
        ):
            return True

    return False


def _get_methods_for_card(
    player,
    card,
    *,
    pay=True,
    discount=0,
    allow_kerker=True,
    allow_kraan=True,
    allow_herbergier=True,
    allow_rechter=True,
    allow_related_free=True,
    game_state=None,
):
    """
    Build the list of PlayMethod options for a single card.

    Adding a new play method (e.g. Rechter) only requires editing this
    function — both get_possible_card_plays and
    get_possible_meadow_card_plays_with_discount pick it up automatically
    through their flag arguments.
    """
    from class_card import Construction, Critter

    methods = []
    needs_own_city_space = card.name != "Dwaas"
    city_fit = True if not needs_own_city_space else player.card_fits_in_city(card)

    is_dwaas = card.name == "Dwaas"
    if is_dwaas and game_state is None:
        return []

    if not pay:
        methods.append(
            PlayMethod(
                method="free_no_pay",
                requires_city_discard=False,
                city_discard_optional=False,
                pay_requirements=None,
            )
        )

    if pay:
        # Resource-paid (with optional discount; discount=0 → full cost only)
        for reduced_cost in _iter_discounted_requirements(
            card.costs,
            discount,
        ):
            if _has_resources(player.resources, reduced_cost):
                methods.append(
                    PlayMethod(
                        method="pay_resources",
                        requires_city_discard=False,
                        city_discard_optional=(discount == 0),
                        pay_requirements=reduced_cost,
                        play_tags=(EXTERNAL_PLAY_ABILITY,) if discount > 0 else (),
                        play_conflicts=(EXTERNAL_PLAY_ABILITY,) if discount > 0 else (),
                    )
                )

        # Free play of critters when related to a played construction
        if allow_related_free and isinstance(card, Critter):
            for constr in player.city:
                if (
                    isinstance(constr, Construction)
                    and card.name in constr.relatedcritters
                    and not constr.relatedoccupied
                ):
                    methods.append(
                        PlayMethod(
                            method="related_free",
                            requires_city_discard=False,
                            city_discard_optional=False,
                            pay_requirements=None,
                            source_card=constr,
                            play_tags=(EXTERNAL_PLAY_ABILITY,),
                        )
                    )

        if allow_kerker:
            methods.extend(_get_kerker_methods(player, card))

        if allow_kraan:
            methods.extend(_get_kraan_methods(player, card))

        if allow_herbergier:
            methods.extend(_get_herbergier_methods(player, card))

        if allow_rechter:
            methods.extend(_get_rechter_methods(player, card))

    if needs_own_city_space and not city_fit:
        on_play_frees_space = _card_can_create_space_before_place(
            player, card, game_state
        )
        if not on_play_frees_space:
            methods = [
                method
                for method in methods
                if getattr(method, "creates_city_space_before_place", False)
            ]

    # Keep only methods compatible with the played card's own on-play effects.
    compatible_methods = []
    for method in methods:
        try:
            build_play_plan(card, method)
            compatible_methods.append(method)
        except ValueError:
            continue

    return compatible_methods


def get_possible_card_plays(
    game_state,
    max_points=99,
    pay=True,
):
    player = game_state["current_player"]
    meadow = game_state["meadow"]
    all_cards = player.hand + meadow.cards
    possible_card_plays: list[PlayCardOption] = []

    for card in all_cards:
        if card.points > max_points:
            continue
        if card.unique and any(c.name == card.name for c in player.city):
            continue
        if not _requirements_met(player, card, game_state):
            continue

        methods = _get_methods_for_card(
            player,
            card,
            pay=pay,
            discount=0,
            allow_kerker=True,
            allow_kraan=True,
            allow_herbergier=True,
            allow_rechter=True,
            allow_related_free=True,
            game_state=game_state,
        )

        final_methods = _dedupe_play_methods(methods)
        if len(final_methods) > 0:
            possible_card_plays.append(PlayCardOption(card=card, methods=final_methods))

    return possible_card_plays


def get_possible_cards(
    game_state,
    max_points=99,
    pay=True,
):
    possible_card_plays = get_possible_card_plays(
        game_state,
        max_points,
        pay,
    )
    possible_cards = [entry.card for entry in possible_card_plays]

    # Remove duplicates while preserving order
    possible_cards = list(dict.fromkeys(possible_cards))
    return possible_cards


def get_possible_locations(game_state):
    player = game_state["current_player"]
    locations = game_state["locations"]
    loc: "Location"
    possible_locations = []

    for loc in locations:
        if not _requirements_met(player, loc, game_state):
            continue

        # Basic locations
        if loc.location_type == "basic" and loc.get_open_spaces() > 0:
            possible_locations.append(loc)

        # Destination cards
        if loc.location_type == "destination_card":
            owner = getattr(loc, "owner", None)
            in_own_city = owner == player
            accessible_open = owner is not None and (owner != player and loc.is_open)

            if loc.get_open_spaces() > 0 and (in_own_city or accessible_open):
                possible_locations.append(loc)

        # Haven locations
        if loc.location_type == "haven" and loc.get_open_spaces() > 0:
            possible_locations.append(loc)

        # Journey locations (autumn only)
        if loc.location_type == "journey":
            in_autumn = player.season == "autumn"
            has_space = loc.get_open_spaces() > 0
            can_discard_required_cards = len(player.hand) >= loc.points

            if in_autumn and has_space and can_discard_required_cards:
                possible_locations.append(loc)

        # Event locations (unclaimed only; claimed events are in player.events)
        if (
            loc.location_type in {"basic_event", "special_event"}
            and loc.get_open_spaces() > 0
        ):
            possible_locations.append(loc)

    # TODO: forest locations

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


def get_possible_meadow_card_plays_with_discount(game_state, discount=3):
    """
    Returns PlayCardOption list for meadow-only cards with a resource discount.

    Only discounted pay_resources methods are offered — related_free is
    excluded (using Herberg when a free play is available is wasteful) and
    Kerker-discount is excluded (Kerker cannot be combined with this effect).
    Any future method added to _get_methods_for_card with allow_* flags will
    be picked up here too once the appropriate flag is added.
    """
    player = game_state["current_player"]
    meadow = game_state["meadow"]

    result = []
    for card in meadow.cards:
        if card.unique and any(c.name == card.name for c in player.city):
            continue
        if not _requirements_met(player, card, game_state):
            continue

        methods = _get_methods_for_card(
            player,
            card,
            pay=True,
            discount=discount,
            allow_kerker=False,
            allow_kraan=False,
            allow_herbergier=False,
            allow_rechter=False,
            allow_related_free=False,
            game_state=game_state,
        )

        final_methods = _dedupe_play_methods(methods)
        if final_methods:
            result.append(PlayCardOption(card=card, methods=final_methods))

    return result


def get_critters_constructions_city(game_state, critter_and_construction):
    from class_card import Construction, Critter

    player = game_state["current_player"]
    critter = critter_and_construction[0]
    construction = critter_and_construction[1]

    options: list[Any] = []
    if critter and not construction:
        options = [c for c in player.city if isinstance(c, Critter)]
    elif construction and not critter:
        options = [c for c in player.city if isinstance(c, Construction)]
    else:
        # If neither flag is set or both are set, allow any card in city
        options = list(player.city)

    return options
