import copy
import uuid
from dataclasses import dataclass
from typing import Any

from actions.base import CompositeAction
from actions.cards import (
    action_cards_from_deck_to_hand,
    action_cards_keep_and_give,
    action_discard_stored_cards,
    action_draw_on_card_type,
    action_give_discard_refill_hand,
    action_play_card,
    action_play_cards_from_deck_or_discardpile,
    action_play_meadow_card_with_discount,
    action_play_revealed_deck_card_for_free,
    action_point_on_location_take_cards,
    action_reactivate_green_card,
    action_refresh_meadow_draw_cards,
    action_remove_card_from_city,
    action_resource_on_card_type,
)
from actions.locations import (
    action_activate_worker_location_for_point_token,
    action_add_destination_card_as_location,
    action_add_destination_if_card_present,
    action_location_copy_action,
    action_remove_destination,
    action_replace_worker,
)
from actions.points import (
    action_place_point_tokens_on_card,
    action_points_for_cards_in_city,
    action_points_for_color_in_city,
    action_points_for_discarding_cards,
    action_points_for_events,
    action_points_for_given_resources,
    action_points_for_payed_resources,
    action_points_for_resources_hand,
    action_points_for_tokens_on_card,
    action_points_general,
)
from actions.resources import (
    action_add_resource_to_other_player,
    action_resource_general,
    action_resource_if_other_card,
    action_resource_if_paired_with_other_card,
    action_resource_per_other_card,
    action_resources_building_costs_discard,
    action_resources_by_choice,
    action_resources_swap,
    action_resources_to_card_storage_choice,
    action_take_all_resources_from_card_storage,
)
from shared.game_types import (
    CardColor,
    CardStorageKey,
    CardType,
    CardZone,
    LocationType,
    PointCategory,
    RequirementKind,
    ResourceType,
)


@dataclass(init=False, eq=False, repr=False)
class Card:
    name: str
    color: CardColor
    costs: dict[ResourceType, int]
    cardsindeck: int
    unique: bool
    points: int
    action_on_play: Any
    action_on_reactivate: Any
    action_on_discard: Any
    action_on_finish: Any
    action_when_card_played: Any
    requirements: Any
    card_storage: dict[CardStorageKey, Any]
    city_space_cost: int
    city_space_group: list[str] | None
    card_id: str

    def __init__(
        self,
        name: str,
        color: CardColor,
        costs: dict[ResourceType, int],
        cardsindeck: int,
        unique: bool,
        points: int,
        action_on_play: Any = None,
        action_on_reactivate: Any = None,
        action_on_discard: Any = None,
        action_on_finish: Any = None,
        action_when_card_played: Any = None,
        requirements: Any = None,
        city_space_cost: int = 1,
        city_space_group: list[str] | None = None,
    ):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Card name must be a non-empty string")
        if not isinstance(color, CardColor):
            raise TypeError("color must be a CardColor")
        if any(not isinstance(resource, ResourceType) for resource in costs):
            raise TypeError("Card costs must use ResourceType keys")
        if set(costs) != set(ResourceType):
            raise ValueError("Card costs must define every ResourceType exactly once")
        if any(type(amount) is not int or amount < 0 for amount in costs.values()):
            raise ValueError("Card resource costs must be non-negative integers")
        self.name = name
        self.color = color
        self.costs = dict(costs)
        self.cardsindeck = cardsindeck
        self.unique = unique
        self.points = points
        self.action_on_play = action_on_play
        self.action_on_reactivate = action_on_reactivate
        self.action_on_discard = action_on_discard
        self.action_on_finish = action_on_finish
        self.action_when_card_played = action_when_card_played
        self.requirements = requirements  # Optional play preconditions
        # Shared storage for effects that keep cards/resources on a card.
        self.card_storage = {
            CardStorageKey.CARDS: [],
            CardStorageKey.RESOURCES: {resource: 0 for resource in ResourceType},
            CardStorageKey.POINT_TOKENS: 0,
        }
        self.city_space_cost = city_space_cost
        self.city_space_group = city_space_group
        self.card_id = str(uuid.uuid4())

    def __str__(self):
        return str(self.name)


class Critter(Card):
    def __init__(
        self,
        name: str,
        color: CardColor,
        costs: dict[ResourceType, int],
        cardsindeck: int,
        unique: bool,
        points: int,
        action_on_play: Any = None,
        action_on_reactivate: Any = None,
        action_on_discard: Any = None,
        action_on_finish: Any = None,
        action_when_card_played: Any = None,
        requirements: Any = None,
        city_space_cost: int = 1,
        city_space_group: list[str] | None = None,
    ):
        super().__init__(
            name,
            color,
            costs,
            cardsindeck,
            unique,
            points,
            action_on_play=action_on_play,
            action_on_reactivate=action_on_reactivate,
            action_on_discard=action_on_discard,
            action_on_finish=action_on_finish,
            action_when_card_played=action_when_card_played,
            requirements=requirements,
            city_space_cost=city_space_cost,
            city_space_group=city_space_group,
        )


class Construction(Card):
    def __init__(
        self,
        name: str,
        color: CardColor,
        costs: dict[ResourceType, int],
        cardsindeck: int,
        unique: bool,
        points: int,
        relatedcritters: list[str],
        action_on_play: Any = None,
        action_on_reactivate: Any = None,
        action_on_discard: Any = None,
        action_on_finish: Any = None,
        action_when_card_played: Any = None,
        requirements: Any = None,
        city_space_cost: int = 1,
        city_space_group: list[str] | None = None,
    ):
        super().__init__(
            name,
            color,
            costs,
            cardsindeck,
            unique,
            points,
            action_on_play=action_on_play,
            action_on_reactivate=action_on_reactivate,
            action_on_discard=action_on_discard,
            action_on_finish=action_on_finish,
            action_when_card_played=action_when_card_played,
            requirements=requirements,
            city_space_cost=city_space_cost,
            city_space_group=city_space_group,
        )
        self.relatedcritters = relatedcritters
        self.relatedoccupied = False


cards_unique: list[Card] = []


# ============================================
# CRITTERS (sorted alphabetically)
# ============================================

architect = Critter(
    name="Architect",
    color=CardColor.PURPLE,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 0, ResourceType.BERRY: 4},
    cardsindeck=2,
    unique=True,
    points=2,
    action_on_finish=action_points_for_resources_hand([ResourceType.RESIN, ResourceType.PEBBLE], 1),
    action_on_discard=action_remove_card_from_city("Architect"),
)

begrafenisondernemer = Critter(
    name="Begrafenisondernemer",
    color=CardColor.TAN,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 0, ResourceType.BERRY: 2},
    cardsindeck=2,
    unique=True,
    points=1,
    action_on_play=CompositeAction(
        [
            action_refresh_meadow_draw_cards(3),
            action_add_destination_if_card_present(
                "Begraafplaats 2",
                LocationType.DESTINATION_CARD,
                1,
                action_play_cards_from_deck_or_discardpile(4),
                check_card_name="Begraafplaats",
                permanent_workers=True,
            ),
        ]
    ),
    action_on_discard=CompositeAction(
        [
            action_remove_destination("Begraafplaats 2"),
            action_remove_card_from_city("Begrafenisondernemer"),
        ]
    ),
)

boswachter = Critter(
    name="Boswachter",
    color=CardColor.TAN,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 0, ResourceType.BERRY: 2},
    cardsindeck=2,
    unique=True,
    points=1,
    action_on_play=action_replace_worker(),
    action_on_discard=action_remove_card_from_city("Boswachter"),
    requirements={"kind": RequirementKind.HAS_PLACED_WORKER},
)

dokter = Critter(
    name="Dokter",
    color=CardColor.GREEN,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 0, ResourceType.BERRY: 4},
    cardsindeck=2,
    unique=True,
    points=4,
    action_on_play=action_points_for_payed_resources(3, ResourceType.BERRY, 1),
    action_on_reactivate=action_points_for_payed_resources(3, ResourceType.BERRY, 1),
    action_on_discard=action_remove_card_from_city("Dokter"),
)

dwaas = Critter(
    name="Dwaas",
    color=CardColor.TAN,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 0, ResourceType.BERRY: 3},
    cardsindeck=2,
    unique=True,
    points=-2,
    action_on_play=None,
    action_on_discard=action_remove_card_from_city("Dwaas"),
    requirements={"kind": RequirementKind.OTHER_PLAYER_HAS_CITY_SPACE},
)

herbergier = Critter(
    name="Herbergier",
    color=CardColor.BLUE,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 0, ResourceType.BERRY: 1},
    cardsindeck=3,
    unique=True,
    points=1,
    action_on_play=None,
    action_on_discard=action_remove_card_from_city("Herbergier"),
)

herder = Critter(
    name="Herder",
    color=CardColor.TAN,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 0, ResourceType.BERRY: 3},
    cardsindeck=2,
    unique=True,
    points=1,
    action_on_play=CompositeAction(
        [
            action_resource_general(ResourceType.BERRY, 3),
            action_add_resource_to_other_player(ResourceType.BERRY, 3),
            action_points_for_tokens_on_card("Kapel"),
        ]
    ),
    action_on_discard=action_remove_card_from_city("Herder"),
)

historicus = Critter(
    name="Historicus",
    color=CardColor.BLUE,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 0, ResourceType.BERRY: 2},
    cardsindeck=3,
    unique=True,
    points=1,
    action_when_card_played=action_draw_on_card_type(1, (CardType.CRITTER, CardType.CONSTRUCTION)),
    action_on_discard=action_remove_card_from_city("Historicus"),
)

houtsnijder = Critter(
    name="Houtsnijder",
    color=CardColor.GREEN,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 0, ResourceType.BERRY: 2},
    cardsindeck=3,
    unique=False,
    points=2,
    action_on_play=action_points_for_payed_resources(3, ResourceType.TWIG, 1),
    action_on_reactivate=action_points_for_payed_resources(3, ResourceType.TWIG, 1),
    action_on_discard=action_remove_card_from_city("Houtsnijder"),
)

kikkerkapitein = Critter(
    name="Kikkerkapitein",
    color=CardColor.GREEN,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 0, ResourceType.BERRY: 2},
    cardsindeck=3,
    unique=False,
    points=1,
    action_on_play=action_resource_per_other_card("Boerderij", ResourceType.TWIG, 2),
    action_on_reactivate=action_resource_per_other_card("Boerderij", ResourceType.TWIG, 2),
    action_on_discard=action_remove_card_from_city("Kikkerkapitein"),
)

leraar = Critter(
    name="Leraar",
    color=CardColor.GREEN,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 0, ResourceType.BERRY: 2},
    cardsindeck=3,
    unique=False,
    points=2,
    action_on_play=action_cards_keep_and_give(1, 1),
    action_on_reactivate=action_cards_keep_and_give(1, 1),
    action_on_discard=action_remove_card_from_city("Leraar"),
)

koning = Critter(
    name="Koning",
    color=CardColor.PURPLE,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 0, ResourceType.BERRY: 6},
    cardsindeck=2,
    unique=True,
    points=4,
    action_on_finish=action_points_for_events(1, 2),
    action_on_discard=action_remove_card_from_city("Koning"),
)

koningin = Critter(
    name="Koningin",
    color=CardColor.RED,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 0, ResourceType.BERRY: 5},
    cardsindeck=2,
    unique=True,
    points=4,
    action_on_play=action_add_destination_card_as_location(
        "Koningin",
        LocationType.DESTINATION_CARD,
        1,
        action_play_card(3, False),
        requirements={
            "kind": RequirementKind.HAS_PLAYABLE_CARD_WITH_MAX_POINTS,
            "max_points": 3,
        },
    ),
    action_on_discard=CompositeAction(
        [
            action_remove_destination("Koningin"),
            action_remove_card_from_city("Koningin"),
        ]
    ),
)

man = Critter(
    name="Man",
    color=CardColor.GREEN,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 0, ResourceType.BERRY: 3},
    cardsindeck=4,
    unique=False,
    points=2,
    action_on_play=action_resource_if_paired_with_other_card(
        "Man", "Vrouw", "Boerderij", [ResourceType.TWIG, ResourceType.RESIN, ResourceType.PEBBLE, ResourceType.BERRY], 1
    ),
    action_on_reactivate=None,  # Action is handled in season.py
    action_on_discard=action_remove_card_from_city("Man"),
    city_space_group=["Man", "Vrouw"],
)

marskramer = Critter(
    name="Marskramer",
    color=CardColor.GREEN,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 0, ResourceType.BERRY: 2},
    cardsindeck=3,
    unique=False,
    points=1,
    action_on_play=action_resources_swap(2),
    action_on_reactivate=action_resources_swap(2),
    action_on_discard=action_remove_card_from_city("Marskramer"),
)

mijnwerkermol = Critter(
    name="Mijnwerkermol",
    color=CardColor.GREEN,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 0, ResourceType.BERRY: 3},
    cardsindeck=3,
    unique=False,
    points=1,
    action_on_play=action_reactivate_green_card(from_own_city=False),
    action_on_reactivate=action_reactivate_green_card(from_own_city=False),
    action_on_discard=action_remove_card_from_city("Mijnwerkermol"),
)

monnik = Critter(
    name="Monnik",
    color=CardColor.GREEN,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 0, ResourceType.BERRY: 1},
    cardsindeck=2,
    unique=True,
    points=0,
    action_on_play=CompositeAction(
        [
            action_points_for_given_resources(
                max_nr_resources=2, resource_type=ResourceType.BERRY, points_per_resource=2
            ),
            action_add_destination_if_card_present(
                "Klooster 2",
                LocationType.DESTINATION_CARD,
                1,
                action_points_for_given_resources(nr_resources=2, points=4),
                check_card_name="Klooster",
                permanent_workers=True,
                requirements={
                    "kind": RequirementKind.HAS_TOTAL_RESOURCES,
                    "amount": 2,
                },
            ),
        ]
    ),
    action_on_reactivate=action_points_for_given_resources(
        max_nr_resources=2, resource_type=ResourceType.BERRY, points_per_resource=2
    ),
    action_on_discard=CompositeAction(
        [
            action_remove_destination("Klooster 2"),
            action_remove_card_from_city("Monnik"),
        ]
    ),
)

postduif = Critter(
    name="Postduif",
    color=CardColor.TAN,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 0, ResourceType.BERRY: 2},
    cardsindeck=3,
    unique=False,
    points=0,
    action_on_play=action_play_revealed_deck_card_for_free(2, 3),
    action_on_discard=action_remove_card_from_city("Postduif"),
    requirements={"kind": RequirementKind.HAS_CITY_SPACE},
)

rechter = Critter(
    name="Rechter",
    color=CardColor.BLUE,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 0, ResourceType.BERRY: 3},
    cardsindeck=2,
    unique=True,
    points=2,
    action_on_discard=action_remove_card_from_city("Rechter"),
)

schoonmaker = Critter(
    name="Schoonmaker",
    color=CardColor.GREEN,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 0, ResourceType.BERRY: 3},
    cardsindeck=3,
    unique=False,
    points=2,
    action_on_play=action_reactivate_green_card(from_own_city=True),
    action_on_reactivate=action_reactivate_green_card(from_own_city=True),
    action_on_discard=action_remove_card_from_city("Schoonmaker"),
)

vrouw = Critter(
    name="Vrouw",
    color=CardColor.PURPLE,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 0, ResourceType.BERRY: 2},
    cardsindeck=4,
    unique=False,
    points=2,
    action_on_finish=None,  # Action is handled in turn.py when game finishes
    action_on_discard=action_remove_card_from_city("Vrouw"),
    city_space_group=["Man", "Vrouw"],
)

winkelier = Critter(
    name="Winkelier",
    color=CardColor.BLUE,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 0, ResourceType.BERRY: 2},
    cardsindeck=3,
    unique=True,
    points=1,
    action_when_card_played=action_resource_on_card_type(ResourceType.BERRY, 1, CardType.CRITTER),
    action_on_discard=action_remove_card_from_city("Winkelier"),
)

zanger = Critter(
    name="Zanger",
    color=CardColor.TAN,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 0, ResourceType.BERRY: 3},
    cardsindeck=2,
    unique=True,
    points=0,
    action_on_play=action_points_for_discarding_cards(5, 1),
    action_on_discard=action_remove_card_from_city("Zanger"),
)

zwerver = Critter(
    name="Zwerver",
    color=CardColor.TAN,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 0, ResourceType.BERRY: 2},
    cardsindeck=3,
    unique=False,
    points=1,
    city_space_cost=0,
    action_on_play=action_cards_from_deck_to_hand(3),
    action_on_discard=action_remove_card_from_city("Zwerver"),
)


cards_unique.append(architect)
cards_unique.append(begrafenisondernemer)
cards_unique.append(boswachter)
cards_unique.append(dokter)
cards_unique.append(dwaas)
cards_unique.append(herder)
cards_unique.append(historicus)
cards_unique.append(herbergier)
cards_unique.append(houtsnijder)
cards_unique.append(kikkerkapitein)
cards_unique.append(koning)
cards_unique.append(koningin)
cards_unique.append(leraar)
cards_unique.append(man)
cards_unique.append(marskramer)
cards_unique.append(mijnwerkermol)
cards_unique.append(monnik)
cards_unique.append(postduif)
cards_unique.append(rechter)
cards_unique.append(schoonmaker)
cards_unique.append(vrouw)
cards_unique.append(winkelier)
cards_unique.append(zanger)
cards_unique.append(zwerver)


# ============================================
# CONSTRUCTIONS (sorted alphabetically)
# ============================================

begraafplaats = Construction(
    name="Begraafplaats",
    color=CardColor.RED,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 2, ResourceType.BERRY: 0},
    cardsindeck=2,
    unique=True,
    points=0,
    relatedcritters=["Begrafenisondernemer"],
    action_on_play=CompositeAction(
        [
            action_add_destination_card_as_location(
                "Begraafplaats 1",
                LocationType.DESTINATION_CARD,
                1,
                action_play_cards_from_deck_or_discardpile(4),
                permanent_workers=True,
                requirements={"kind": RequirementKind.HAS_CITY_SPACE},
            ),
            action_add_destination_if_card_present(
                "Begraafplaats 2",
                LocationType.DESTINATION_CARD,
                1,
                action_play_cards_from_deck_or_discardpile(4),
                check_card_name="Begrafenisondernemer",
                permanent_workers=True,
                requirements={"kind": RequirementKind.HAS_CITY_SPACE},
            ),
        ]
    ),
    action_on_discard=CompositeAction(
        [
            action_remove_destination("Begraafplaats 1"),
            action_remove_destination("Begraafplaats 2"),
            action_remove_card_from_city("Begraafplaats"),
        ]
    ),
    requirements={"kind": RequirementKind.HAS_CITY_SPACE},
)


boerderij = Construction(
    name="Boerderij",
    color=CardColor.GREEN,
    costs={ResourceType.TWIG: 2, ResourceType.RESIN: 1, ResourceType.PEBBLE: 0, ResourceType.BERRY: 0},
    cardsindeck=8,
    unique=False,
    points=1,
    relatedcritters=["Man", "Vrouw"],
    action_on_play=action_resource_general(ResourceType.BERRY, 1),
    action_on_reactivate=action_resource_general(ResourceType.BERRY, 1),
    action_on_discard=action_remove_card_from_city("Boerderij"),
)

evertree = Construction(
    name="Evertree",
    color=CardColor.PURPLE,
    costs={ResourceType.TWIG: 3, ResourceType.RESIN: 3, ResourceType.PEBBLE: 3, ResourceType.BERRY: 0},
    cardsindeck=2,
    unique=True,
    points=5,
    relatedcritters=[
        "Architect",
        "Begrafenisondernemer",
        "Boswachter",
        "Dokter",
        "Dwaas",
        "Herbergier",
        "Herder",
        "Historicus",
        "Houtsnijder",
        "Kikkerkapitein",
        "Koning",
        "Koningin",
        "Leraar",
        "Man",
        "Marskramer",
        "Mijnwerkermol",
        "Monnik",
        "Postduif",
        "Rechter",
        "Schoonmaker",
        "Vrouw",
        "Winkelier",
        "Zanger",
        "Zwerver",
    ],
    action_on_finish=action_points_for_color_in_city(CardColor.PURPLE, 1),
    action_on_discard=action_remove_card_from_city("Evertree"),
)

gerechtsgebouw = Construction(
    name="Gerechtsgebouw",
    color=CardColor.BLUE,
    costs={ResourceType.TWIG: 1, ResourceType.RESIN: 1, ResourceType.PEBBLE: 2, ResourceType.BERRY: 0},
    cardsindeck=2,
    unique=True,
    points=2,
    relatedcritters=["Rechter"],
    action_when_card_played=action_resource_on_card_type(
        [ResourceType.TWIG, ResourceType.RESIN, ResourceType.PEBBLE], 1, CardType.CONSTRUCTION
    ),
    action_on_discard=action_remove_card_from_city("Gerechtsgebouw"),
)

harsraffinaderij = Construction(
    name="Harsraffinaderij",
    color=CardColor.GREEN,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 1, ResourceType.PEBBLE: 1, ResourceType.BERRY: 0},
    cardsindeck=3,
    unique=False,
    points=1,
    relatedcritters=["Schoonmaker"],
    action_on_play=action_resource_general(ResourceType.RESIN, 1),
    action_on_reactivate=action_resource_general(ResourceType.RESIN, 1),
    action_on_discard=action_remove_card_from_city("Harsraffinaderij"),
)

herberg = Construction(
    name="Herberg",
    color=CardColor.RED,
    costs={ResourceType.TWIG: 2, ResourceType.RESIN: 1, ResourceType.PEBBLE: 0, ResourceType.BERRY: 0},
    cardsindeck=3,
    unique=False,
    points=2,
    relatedcritters=["Herbergier"],
    action_on_play=action_add_destination_card_as_location(
        "Herberg",
        LocationType.DESTINATION_CARD,
        1,
        action_play_meadow_card_with_discount(3),
        is_open=True,
        requirements={"kind": RequirementKind.HAS_PLAYABLE_MEADOW_CARD, "discount": 3},
    ),
    action_on_discard=CompositeAction(
        [action_remove_destination("Herberg"), action_remove_card_from_city("Herberg")]
    ),
)

kapel = Construction(
    name="Kapel",
    color=CardColor.RED,
    costs={ResourceType.TWIG: 2, ResourceType.RESIN: 1, ResourceType.PEBBLE: 1, ResourceType.BERRY: 0},
    cardsindeck=2,
    unique=True,
    points=2,
    relatedcritters=["Herder"],
    action_on_play=action_add_destination_card_as_location(
        "Kapel",
        LocationType.DESTINATION_CARD,
        1,
        action_point_on_location_take_cards("Kapel", 1, 2),
    ),
    action_on_discard=CompositeAction(
        [action_remove_destination("Kapel"), action_remove_card_from_city("Kapel")]
    ),
)

kasteel = Construction(
    name="Kasteel",
    color=CardColor.PURPLE,
    costs={ResourceType.TWIG: 2, ResourceType.RESIN: 3, ResourceType.PEBBLE: 3, ResourceType.BERRY: 0},
    cardsindeck=2,
    unique=True,
    points=4,
    relatedcritters=["Koning"],
    action_on_finish=action_points_for_cards_in_city("Construction", False, 1),
    action_on_discard=action_remove_card_from_city("Kasteel"),
)

kerker = Construction(
    name="Kerker",
    color=CardColor.BLUE,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 1, ResourceType.PEBBLE: 2, ResourceType.BERRY: 0},
    cardsindeck=2,
    unique=True,
    points=0,
    relatedcritters=["Boswachter"],
    action_on_discard=CompositeAction(
        [action_discard_stored_cards("Kerker"), action_remove_card_from_city("Kerker")]
    ),
)

kermis = Construction(
    name="Kermis",
    color=CardColor.GREEN,
    costs={ResourceType.TWIG: 1, ResourceType.RESIN: 2, ResourceType.PEBBLE: 1, ResourceType.BERRY: 0},
    cardsindeck=3,
    unique=False,
    points=3,
    relatedcritters=["Dwaas"],
    action_on_play=action_cards_from_deck_to_hand(2),
    action_on_reactivate=action_cards_from_deck_to_hand(2),
    action_on_discard=action_remove_card_from_city("Kermis"),
)

klokkentoren = Construction(
    name="Klokkentoren",
    color=CardColor.BLUE,
    costs={ResourceType.TWIG: 3, ResourceType.RESIN: 0, ResourceType.PEBBLE: 1, ResourceType.BERRY: 0},
    cardsindeck=3,
    unique=True,
    points=0,
    relatedcritters=["Historicus"],
    action_on_play=action_place_point_tokens_on_card(3),
    action_on_reactivate=None,  # Action is handled in season.py (every season change)
    action_on_discard=action_remove_card_from_city("Klokkentoren"),
)

klooster = Construction(
    name="Klooster",
    color=CardColor.RED,
    costs={ResourceType.TWIG: 1, ResourceType.RESIN: 1, ResourceType.PEBBLE: 1, ResourceType.BERRY: 0},
    cardsindeck=2,
    unique=True,
    points=1,
    relatedcritters=["Monnik"],
    action_on_play=CompositeAction(
        [
            action_add_destination_card_as_location(
                "Klooster 1",
                LocationType.DESTINATION_CARD,
                1,
                action_points_for_given_resources(nr_resources=2, points=4),
                permanent_workers=True,
                requirements={"kind": RequirementKind.HAS_TOTAL_RESOURCES, "amount": 2},
            ),
            action_add_destination_if_card_present(
                "Klooster 2",
                LocationType.DESTINATION_CARD,
                1,
                action_points_for_given_resources(nr_resources=2, points=4),
                check_card_name="Monnik",
                permanent_workers=True,
                requirements={"kind": RequirementKind.HAS_TOTAL_RESOURCES, "amount": 2},
            ),
        ]
    ),
    action_on_discard=CompositeAction(
        [
            action_remove_destination("Klooster 1"),
            action_remove_destination("Klooster 2"),
            action_remove_card_from_city("Klooster"),
        ]
    ),
)

kraan = Construction(
    name="Kraan",
    color=CardColor.BLUE,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 1, ResourceType.BERRY: 0},
    cardsindeck=3,
    unique=True,
    points=1,
    relatedcritters=["Architect"],
    action_on_discard=action_remove_card_from_city("Kraan"),
)

mijn = Construction(
    name="Mijn",
    color=CardColor.GREEN,
    costs={ResourceType.TWIG: 1, ResourceType.RESIN: 1, ResourceType.PEBBLE: 1, ResourceType.BERRY: 0},
    cardsindeck=3,
    unique=False,
    points=2,
    relatedcritters=["Mijnwerkermol"],
    action_on_play=action_resource_general(ResourceType.PEBBLE, 1),
    action_on_reactivate=action_resource_general(ResourceType.PEBBLE, 1),
    action_on_discard=action_remove_card_from_city("Mijn"),
)

pakhuis = Construction(
    name="Pakhuis",
    color=CardColor.GREEN,
    costs={ResourceType.TWIG: 1, ResourceType.RESIN: 1, ResourceType.PEBBLE: 1, ResourceType.BERRY: 0},
    cardsindeck=3,
    unique=False,
    points=2,
    relatedcritters=["Houtsnijder"],
    action_on_play=CompositeAction(
        [
            action_resources_to_card_storage_choice(
                "Pakhuis", {ResourceType.TWIG: 3, ResourceType.RESIN: 2, ResourceType.PEBBLE: 1, ResourceType.BERRY: 2}
            ),
            action_add_destination_card_as_location(
                "Pakhuis",
                LocationType.DESTINATION_CARD,
                1,
                action_take_all_resources_from_card_storage("Pakhuis"),
            ),
        ]
    ),
    action_on_reactivate=action_resources_to_card_storage_choice(
        "Pakhuis", {ResourceType.TWIG: 3, ResourceType.RESIN: 2, ResourceType.PEBBLE: 1, ResourceType.BERRY: 2}
    ),
    action_on_discard=CompositeAction(
        [
            action_remove_destination("Pakhuis"),
            action_remove_card_from_city("Pakhuis"),
        ]
    ),
)

paleis = Construction(
    name="Paleis",
    color=CardColor.PURPLE,
    costs={ResourceType.TWIG: 2, ResourceType.RESIN: 3, ResourceType.PEBBLE: 3, ResourceType.BERRY: 0},
    cardsindeck=2,
    unique=True,
    points=4,
    relatedcritters=["Koningin"],
    action_on_finish=action_points_for_cards_in_city("Construction", True, 1),
    action_on_discard=action_remove_card_from_city("Paleis"),
)

postkantoor = Construction(
    name="Postkantoor",
    color=CardColor.RED,
    costs={ResourceType.TWIG: 1, ResourceType.RESIN: 2, ResourceType.PEBBLE: 0, ResourceType.BERRY: 0},
    cardsindeck=3,
    unique=False,
    points=2,
    relatedcritters=["Postduif"],
    action_on_play=action_add_destination_card_as_location(
        "Postkantoor",
        LocationType.DESTINATION_CARD,
        1,
        action_give_discard_refill_hand(2),
        is_open=True,
        requirements=[
            {"kind": RequirementKind.HAS_HAND_CARDS, "amount": 2},
            {"kind": RequirementKind.OTHER_PLAYER_HAS_HAND_SPACE, "amount": 2},
        ],
    ),
    action_on_discard=CompositeAction(
        [
            action_remove_destination("Postkantoor"),
            action_remove_card_from_city("Postkantoor"),
        ]
    ),
)

ruines = Construction(
    name="Ruines",
    color=CardColor.TAN,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 0, ResourceType.PEBBLE: 0, ResourceType.BERRY: 0},
    cardsindeck=3,
    unique=False,
    points=0,
    relatedcritters=["Marskramer"],
    action_on_play=CompositeAction(
        [
            action_resources_building_costs_discard(False, True),
            action_cards_from_deck_to_hand(2),
        ],
    ),
    action_on_discard=action_remove_card_from_city("Ruines"),
    requirements={
        "kind": RequirementKind.MIN_CARDS_OF_TYPE,
        "card_type": CardType.CONSTRUCTION,
        "area": CardZone.CITY,
        "count": 1,
    },
)

school = Construction(
    name="School",
    color=CardColor.PURPLE,
    costs={ResourceType.TWIG: 2, ResourceType.RESIN: 2, ResourceType.PEBBLE: 0, ResourceType.BERRY: 0},
    cardsindeck=2,
    unique=True,
    points=2,
    relatedcritters=["Leraar"],
    action_on_finish=action_points_for_cards_in_city("Critter", False, 1),
    action_on_discard=action_remove_card_from_city("School"),
)

takkenboot = Construction(
    name="Takkenboot",
    color=CardColor.GREEN,
    costs={ResourceType.TWIG: 1, ResourceType.RESIN: 0, ResourceType.PEBBLE: 1, ResourceType.BERRY: 0},
    cardsindeck=3,
    unique=False,
    points=1,
    relatedcritters=["Kikkerkapitein"],
    action_on_play=action_resource_general(ResourceType.TWIG, 2),
    action_on_reactivate=action_resource_general(ResourceType.TWIG, 2),
    action_on_discard=action_remove_card_from_city("Takkenboot"),
)

theater = Construction(
    name="Theater",
    color=CardColor.PURPLE,
    costs={ResourceType.TWIG: 3, ResourceType.RESIN: 1, ResourceType.PEBBLE: 1, ResourceType.BERRY: 0},
    cardsindeck=2,
    unique=True,
    points=3,
    relatedcritters=["Zanger"],
    action_on_finish=action_points_for_cards_in_city("Critter", True, 1),
    action_on_discard=action_remove_card_from_city("Theater"),
)

uitkijkpost = Construction(
    name="Uitkijkpost",
    color=CardColor.RED,
    costs={ResourceType.TWIG: 1, ResourceType.RESIN: 1, ResourceType.PEBBLE: 1, ResourceType.BERRY: 0},
    cardsindeck=2,
    unique=True,
    points=2,
    relatedcritters=["Zwerver"],
    action_on_play=action_add_destination_card_as_location(
        "Uitkijkpost",
        LocationType.DESTINATION_CARD,
        1,
        action_location_copy_action([LocationType.BASIC, LocationType.FOREST]),
    ),
    action_on_discard=CompositeAction(
        [
            action_remove_destination("Uitkijkpost"),
            action_remove_card_from_city("Uitkijkpost"),
        ]
    ),
)

universiteit = Construction(
    name="Universiteit",
    color=CardColor.RED,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 1, ResourceType.PEBBLE: 2, ResourceType.BERRY: 0},
    cardsindeck=2,
    unique=True,
    points=3,
    relatedcritters=["Dokter"],
    action_on_play=action_add_destination_card_as_location(
        "Universiteit",
        LocationType.DESTINATION_CARD,
        1,
        CompositeAction(
            [
                action_resources_building_costs_discard(True, True),
                action_resources_by_choice([ResourceType.TWIG, ResourceType.RESIN, ResourceType.PEBBLE, ResourceType.BERRY], 1),
                action_points_general(PointCategory.TOKEN, 1),
            ]
        ),
        requirements={"kind": RequirementKind.HAS_CITY_CARDS, "amount": 1},
    ),
    action_on_discard=CompositeAction(
        [
            action_remove_destination("Universiteit"),
            action_remove_card_from_city("Universiteit"),
        ]
    ),
)

winkel = Construction(
    name="Winkel",
    color=CardColor.GREEN,
    costs={ResourceType.TWIG: 0, ResourceType.RESIN: 1, ResourceType.PEBBLE: 1, ResourceType.BERRY: 0},
    cardsindeck=3,
    unique=False,
    points=1,
    relatedcritters=["Winkelier"],
    action_on_play=CompositeAction(
        [
            action_resource_general(ResourceType.BERRY, 1),
            action_resource_if_other_card("Boerderij", ResourceType.BERRY, 1),
        ]
    ),
    action_on_reactivate=CompositeAction(
        [
            action_resource_general(ResourceType.BERRY, 1),
            action_resource_if_other_card("Boerderij", ResourceType.BERRY, 1),
        ]
    ),
    action_on_discard=action_remove_card_from_city("Winkel"),
)


cards_unique.append(begraafplaats)
cards_unique.append(boerderij)
cards_unique.append(evertree)
cards_unique.append(gerechtsgebouw)
cards_unique.append(harsraffinaderij)
cards_unique.append(herberg)
cards_unique.append(kapel)
cards_unique.append(kasteel)
cards_unique.append(kerker)
cards_unique.append(kermis)
cards_unique.append(klokkentoren)
cards_unique.append(klooster)
cards_unique.append(kraan)
cards_unique.append(mijn)
cards_unique.append(pakhuis)
cards_unique.append(paleis)
cards_unique.append(postkantoor)
cards_unique.append(ruines)
cards_unique.append(school)
cards_unique.append(takkenboot)
cards_unique.append(theater)
cards_unique.append(universiteit)
cards_unique.append(uitkijkpost)
cards_unique.append(winkel)


# ============================================
# INITIATE CARDS WITH THE RIGHT QUANTITY
# ============================================

init_cards = []
for c in cards_unique:
    for _ in range(c.cardsindeck):
        card_copy = copy.deepcopy(c)
        card_copy.card_id = str(uuid.uuid4())
        init_cards.append(card_copy)
