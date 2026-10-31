from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from actions.base import CompositeAction
from actions.cards import (
    action_cards_from_deck_to_hand_or_location,
    action_cards_from_deck_to_hand,
    action_discard_cards_from_city,
    action_discard_cards_from_hand,
    action_discard_cards_for_deck_cards,
    action_play_two_meadow_cards_with_discount,
    action_reactivate_all_green_cards,
    action_store_critter_cards,
)
from actions.locations import action_retake_worker
from actions.points import (
    action_points_for_given_resources,
    action_points_for_city_assets,
    action_points_for_resources_event_location,
    action_points_for_cards_in_event_location,
    action_points_for_tokens_on_card,
    action_points_general,
)
from actions.locations import action_location_copy_action
from actions.resources import (
    action_resource_general,
    action_resources_by_choice,
    action_resources_by_choice_for_card_tokens,
    action_resources_for_cards,
    action_resources_to_location,
)
from shared.game_types import (
    CardColor,
    CardStorageKey,
    CardType,
    CardZone,
    CityAssetType,
    LocationType,
    PointCategory,
    RequirementKind,
    ResourceType,
)

if TYPE_CHECKING:
    from class_card import Card
    from class_player import Player


@dataclass(init=False, eq=False, repr=False)
class Location:
    name: str
    location_type: LocationType
    maxworkers: int
    action_on_place_worker: Any
    is_open: bool
    action_on_finish: Any
    workers: dict["Player", int]
    resources: dict[ResourceType, int]
    card_storage: dict[CardStorageKey, Any]
    permanent_workers: bool
    owner: "Player | None"
    points: int
    requirements: Any
    source_card_id: str | None

    def __init__(
        self,
        name: str,
        location_type: LocationType,
        maxworkers: int,
        action_on_place_worker: Any,
        *,
        is_open: bool = False,
        action_on_finish: Any = None,
        permanent_workers: bool = False,
        owner: "Player | None" = None,
        points: int = 0,
        requirements: Any = None,
        source_card_id: str | None = None,
    ):
        if not isinstance(location_type, LocationType):
            raise TypeError("location_type must be a LocationType")
        self.name = name
        self.location_type = location_type  # For example basic, journey, haven
        self.is_open = is_open  # Attribute for destination cards
        self.maxworkers = maxworkers
        self.action_on_place_worker = action_on_place_worker
        self.action_on_finish = action_on_finish
        self.workers: dict["Player", int] = {}
        self.resources = {resource: 0 for resource in ResourceType}
        self.card_storage: dict[CardStorageKey, Any] = {CardStorageKey.CARDS: []}
        self.permanent_workers = permanent_workers
        self.owner = owner  # Player that owns this destination location
        self.points = points
        self.requirements = requirements
        self.source_card_id = source_card_id

    def __str__(self):
        return str(self.name)

    # Function to add a worker from a player
    def add_worker(self, player: "Player"):
        if player not in self.workers:
            self.workers[player] = 0
        self.workers[player] += 1

    # Function to remove a worker from a player
    def remove_worker(self, player: "Player"):
        self.workers[player] -= 1
        if self.workers[player] == 0:
            del self.workers[player]

    # Function to check open spaces for workers
    def get_open_spaces(self):
        total_workers = sum(self.workers.values())
        return self.maxworkers - total_workers

    # Function to get workers of a specific player
    def get_player_workers(self, player: "Player"):
        return self.workers.get(player, 0)

    # Function to add resources to a specific category
    def resources_add(
        self, resource: ResourceType, amount: int
    ) -> dict[ResourceType, int]:
        if not isinstance(resource, ResourceType):
            raise TypeError("resource must be a ResourceType")
        self.resources[resource] += amount
        return self.resources

    # Function to remove resources from a specific category
    def resources_remove(
        self, resource: ResourceType, amount: int
    ) -> dict[ResourceType, int]:
        if not isinstance(resource, ResourceType):
            raise TypeError("resource must be a ResourceType")
        self.resources[resource] -= amount
        return self.resources


init_locations = []


# ============================================
# TEMPORARY AND PERMANENT
# ============================================

# A temporary location is added which can be used when a location is removed
# and already placed workers need to be stored somewhere temporarily.
temp = Location("Temporary", LocationType.TEMPORARY, 0, None)

# A permanent location is added which can be used when a permanent location
# is removed and already placed workers need to be stored somewhere.
permanent = Location(
    "Permanent", LocationType.PERMANENT, 0, None, permanent_workers=True
)

init_locations.append(temp)
init_locations.append(permanent)


# ============================================
# BASIC
# ============================================

twigs = Location(
    "Three_twigs", LocationType.BASIC, 1, action_resource_general(ResourceType.TWIG, 3)
)
resins = Location(
    "Two_resins", LocationType.BASIC, 1, action_resource_general(ResourceType.RESIN, 2)
)
pebble = Location(
    "One_pebble", LocationType.BASIC, 1, action_resource_general(ResourceType.PEBBLE, 1)
)
berry = Location(
    "One_berry", LocationType.BASIC, 99, action_resource_general(ResourceType.BERRY, 1)
)

twigs_card = Location(
    "Twigs_Card",
    LocationType.BASIC,
    99,
    CompositeAction(
        [
            action_resource_general(ResourceType.TWIG, 2),
            action_cards_from_deck_to_hand(1),
        ]
    ),
)
resin_card = Location(
    "Resin_Card",
    LocationType.BASIC,
    99,
    CompositeAction(
        [
            action_resource_general(ResourceType.RESIN, 1),
            action_cards_from_deck_to_hand(1),
        ]
    ),
)
cards_point = Location(
    "Cards_Point",
    LocationType.BASIC,
    99,
    CompositeAction(
        [
            action_points_general(PointCategory.TOKEN, 1),
            action_cards_from_deck_to_hand(2),
        ]
    ),
)
berry_card = Location(
    "Berry_Card",
    LocationType.BASIC,
    1,
    CompositeAction(
        [
            action_resource_general(ResourceType.BERRY, 1),
            action_cards_from_deck_to_hand(1),
        ]
    ),
)

init_locations.extend([twigs, resins, pebble, berry])
init_locations.extend([twigs_card, resin_card, cards_point, berry_card])


# ============================================
# FOREST
# ============================================

forest_locations: list[Location] = []

cards_for_resources = Location(
    "Cards_For_Resources",
    LocationType.FOREST,
    1,
    action_resources_for_cards(max_discard=3, cards_per_resource=1),
    requirements={"kind": RequirementKind.HAS_HAND_CARDS, "amount": 1},
)
card_for_cards = Location(
    "Cards_For_Cards",
    LocationType.FOREST,
    1,
    action_discard_cards_for_deck_cards(),
    requirements={"kind": RequirementKind.HAS_HAND_CARDS, "amount": 1},
)
card_from_meadow = Location(
    "Card_From_Meadow",
    LocationType.FOREST,
    1,
    action_play_two_meadow_cards_with_discount(),
    requirements=[
        {"kind": RequirementKind.HAS_CITY_SPACE},
        {"kind": RequirementKind.HAS_PLAYABLE_MEADOW_CARD, "discount": 1},
    ],
)
copy_basic_location = Location(
    "Copy_Basic",
    LocationType.FOREST,
    1,
    CompositeAction(
        [
            action_location_copy_action([LocationType.BASIC]),
            action_cards_from_deck_to_hand(1),
        ]
    ),
)
two_resources = Location(
    "Two_resources",
    LocationType.FOREST,
    1,
    action_resources_by_choice(
        [
            ResourceType.TWIG,
            ResourceType.RESIN,
            ResourceType.PEBBLE,
            ResourceType.BERRY,
        ],
        2,
    ),
)
cards_resource = Location(
    "Cards_Resource",
    LocationType.FOREST,
    1,
    CompositeAction(
        [
            action_resources_by_choice(
                [
                    ResourceType.TWIG,
                    ResourceType.RESIN,
                    ResourceType.PEBBLE,
                    ResourceType.BERRY,
                ],
                1,
            ),
            action_cards_from_deck_to_hand(2),
        ]
    ),
)
twig_resin_berry = Location(
    "Twig_Resin_Berry",
    LocationType.FOREST,
    1,
    CompositeAction(
        [
            action_resource_general(ResourceType.TWIG, 1),
            action_resource_general(ResourceType.RESIN, 1),
            action_resource_general(ResourceType.BERRY, 1),
        ]
    ),
)
cards_pebble = Location(
    "Cards_Pebble",
    LocationType.FOREST,
    1,
    CompositeAction(
        [
            action_resource_general(ResourceType.PEBBLE, 1),
            action_cards_from_deck_to_hand(3),
        ]
    ),
)
berries_card = Location(
    "Berries_Card",
    LocationType.FOREST,
    1,
    CompositeAction(
        [
            action_resource_general(ResourceType.BERRY, 2),
            action_cards_from_deck_to_hand(1),
        ]
    ),
)
resins_twig = Location(
    "Resins_Twig",
    LocationType.FOREST,
    1,
    CompositeAction(
        [
            action_resource_general(ResourceType.RESIN, 2),
            action_resource_general(ResourceType.TWIG, 1),
        ]
    ),
)
berries = Location(
    "Three_berries",
    LocationType.FOREST,
    1,
    action_resource_general(ResourceType.BERRY, 3),
)


forest_locations.extend(
    [
        cards_for_resources,
        card_for_cards,
        card_from_meadow,
        copy_basic_location,
        cards_resource,
        two_resources,
        twig_resin_berry,
        cards_pebble,
        berries_card,
        resins_twig,
        berries,
    ]
)


# ============================================
# BASIC EVENTS
# ============================================
monument = Location(
    "Monument",
    LocationType.BASIC_EVENT,
    1,
    None,
    action_on_finish=action_points_general(PointCategory.EVENT, 3),
    requirements={
        "kind": RequirementKind.MIN_COLOR_CARDS,
        "color": CardColor.BLUE,
        "count": 3,
    },
)
tour = Location(
    "Tour",
    LocationType.BASIC_EVENT,
    1,
    None,
    action_on_finish=action_points_general(PointCategory.EVENT, 3),
    requirements={
        "kind": RequirementKind.MIN_COLOR_CARDS,
        "color": CardColor.RED,
        "count": 3,
    },
)
festival = Location(
    "Festival",
    LocationType.BASIC_EVENT,
    1,
    None,
    action_on_finish=action_points_general(PointCategory.EVENT, 3),
    requirements={
        "kind": RequirementKind.MIN_COLOR_CARDS,
        "color": CardColor.GREEN,
        "count": 4,
    },
)
expedition = Location(
    "Expedition",
    LocationType.BASIC_EVENT,
    1,
    None,
    action_on_finish=action_points_general(PointCategory.EVENT, 3),
    requirements={
        "kind": RequirementKind.MIN_COLOR_CARDS,
        "color": CardColor.TAN,
        "count": 3,
    },
)

init_locations.extend([monument, tour, festival, expedition])


# ============================================
# SPECIAL EVENTS
# ============================================

special_events = []


behe = Location(
    "Behe",
    LocationType.SPECIAL_EVENT,
    1,
    None,
    action_on_finish=action_points_for_city_assets(
        CityAssetType.DESTINATION_WORKERS, 3, card_name="Begraafplaats"
    ),
    requirements={
        "kind": RequirementKind.REQUIRED_CARDS_IN_CITY,
        "cards": ["Begraafplaats", "Herder"],
    },
)

beki = Location(
    "Beki",
    LocationType.SPECIAL_EVENT,
    1,
    CompositeAction(
        [
            action_resource_general(ResourceType.BERRY, -2),
            action_discard_cards_from_city(2),
        ]
    ),
    action_on_finish=action_points_general(PointCategory.EVENT, 6),
    requirements=[
        {
            "kind": RequirementKind.REQUIRED_CARDS_IN_CITY,
            "cards": ["Begrafenisondernemer", "Kikkerkapitein"],
        },
        {"kind": RequirementKind.HAS_CITY_CARDS, "amount": 2},
        {
            "kind": RequirementKind.HAS_RESOURCE_TYPE,
            "resource": ResourceType.BERRY,
            "amount": 2,
        },
    ],
)

dopo = Location(
    "Dopo",
    LocationType.SPECIAL_EVENT,
    1,
    None,
    action_on_finish=action_points_for_city_assets(
        CityAssetType.CARD_PAIRS, 3, paired_card_names=("Man", "Vrouw")
    ),
    requirements={
        "kind": RequirementKind.REQUIRED_CARDS_IN_CITY,
        "cards": ["Dokter", "Postduif"],
    },
)

gebo = Location(
    "Gebo",
    LocationType.SPECIAL_EVENT,
    1,
    action_store_critter_cards(CardZone.CITY, 2),
    action_on_finish=action_points_for_cards_in_event_location(3),
    requirements=[
        {
            "kind": RequirementKind.REQUIRED_CARDS_IN_CITY,
            "cards": ["Gerechtsgebouw", "Boswachter"],
        },
        {
            "kind": RequirementKind.MIN_CARDS_OF_TYPE,
            "card_type": CardType.CRITTER,
            "area": CardZone.CITY,
            "count": 1,
        },
    ],
)

heza = Location(
    "Heza",
    LocationType.SPECIAL_EVENT,
    1,
    action_resources_to_location(
        "Heza", [ResourceType.BERRY], 3, {ResourceType.BERRY: 2}
    ),
    action_on_finish=action_points_for_resources_event_location(
        [ResourceType.BERRY], 2, location_name="Heza"
    ),
    requirements=[
        {
            "kind": RequirementKind.REQUIRED_CARDS_IN_CITY,
            "cards": ["Herberg", "Zanger"],
        },
        {
            "kind": RequirementKind.HAS_RESOURCE_TYPE,
            "resource": ResourceType.BERRY,
            "amount": 1,
        },
    ],
)

hiru = Location(
    "Hiru",
    LocationType.SPECIAL_EVENT,
    1,
    action_cards_from_deck_to_hand_or_location(5, "Hiru"),
    action_on_finish=action_points_for_cards_in_event_location(),
    requirements={
        "kind": RequirementKind.REQUIRED_CARDS_IN_CITY,
        "cards": ["Historicus", "Ruines"],
    },
)

hoka = Location(
    "Hoka",
    LocationType.SPECIAL_EVENT,
    1,
    CompositeAction(
        [
            action_cards_from_deck_to_hand(1),
            action_resources_by_choice_for_card_tokens(
                "Kapel",
                [
                    ResourceType.TWIG,
                    ResourceType.RESIN,
                    ResourceType.PEBBLE,
                    ResourceType.BERRY,
                ],
            ),
        ]
    ),
    action_on_finish=action_points_for_tokens_on_card(
        "Kapel", points_per_token=2, category=PointCategory.EVENT
    ),
    requirements={
        "kind": RequirementKind.REQUIRED_CARDS_IN_CITY,
        "cards": ["Houtsnijder", "Kapel"],
    },
)

klzw = Location(
    "Klzw",
    LocationType.SPECIAL_EVENT,
    1,
    None,
    action_on_finish=action_points_for_city_assets(
        CityAssetType.DESTINATION_WORKERS, 3, card_name="Klooster"
    ),
    requirements={
        "kind": RequirementKind.REQUIRED_CARDS_IN_CITY,
        "cards": ["Klooster", "Zwerver"],
    },
)

leun = Location(
    "Leun",
    LocationType.SPECIAL_EVENT,
    1,
    action_store_critter_cards(CardZone.HAND, 3),
    action_on_finish=action_points_for_cards_in_event_location(2),
    requirements=[
        {
            "kind": RequirementKind.REQUIRED_CARDS_IN_CITY,
            "cards": ["Leraar", "Universiteit"],
        },
        {
            "kind": RequirementKind.MIN_CARDS_OF_TYPE,
            "card_type": CardType.CRITTER,
            "area": CardZone.HAND,
            "count": 1,
        },
    ],
)

mawi = Location(
    "Mawi",
    LocationType.SPECIAL_EVENT,
    1,
    action_resources_to_location(
        "Mawi",
        [
            ResourceType.BERRY,
            ResourceType.TWIG,
            ResourceType.RESIN,
            ResourceType.PEBBLE,
        ],
        3,
        points_per_resource={
            ResourceType.BERRY: 1,
            ResourceType.TWIG: 1,
            ResourceType.RESIN: 2,
            ResourceType.PEBBLE: 2,
        },
    ),
    action_on_finish=action_points_for_resources_event_location(
        [
            ResourceType.BERRY,
            ResourceType.TWIG,
            ResourceType.RESIN,
            ResourceType.PEBBLE,
        ],
        {
            ResourceType.BERRY: 1,
            ResourceType.TWIG: 1,
            ResourceType.RESIN: 2,
            ResourceType.PEBBLE: 2,
        },
        location_name="Mawi",
    ),
    requirements=[
        {
            "kind": RequirementKind.REQUIRED_CARDS_IN_CITY,
            "cards": ["Marskramer", "Winkel"],
        },
        {"kind": RequirementKind.HAS_ANY_RESOURCE},
    ],
)

moke = Location(
    "Moke",
    LocationType.SPECIAL_EVENT,
    1,
    None,
    action_on_finish=action_points_for_city_assets(
        CityAssetType.STORED_CARDS, 3, card_name="Kerker"
    ),
    requirements={
        "kind": RequirementKind.REQUIRED_CARDS_IN_CITY,
        "cards": ["Monnik", "Kerker"],
    },
)

reko = Location(
    "Reko",
    LocationType.SPECIAL_EVENT,
    1,
    action_reactivate_all_green_cards(),
    action_on_finish=action_points_general(PointCategory.EVENT, 3),
    requirements=[
        {
            "kind": RequirementKind.REQUIRED_CARDS_IN_CITY,
            "cards": ["Rechter", "Koningin"],
        },
    ],
)

sckl = Location(
    "Sckl",
    LocationType.SPECIAL_EVENT,
    1,
    action_retake_worker(),
    action_on_finish=action_points_general(PointCategory.EVENT, 4),
    requirements=[
        {
            "kind": RequirementKind.REQUIRED_CARDS_IN_CITY,
            "cards": ["Schoonmaker", "Klokkentoren"],
        },
        {"kind": RequirementKind.HAS_PLACED_WORKER},
    ],
)

twve = Location(
    "Twve",
    LocationType.SPECIAL_EVENT,
    1,
    None,
    action_on_finish=action_points_general(PointCategory.EVENT, 9),
    requirements=[
        {"kind": RequirementKind.MIN_COLOR_CARDS, "color": color, "count": 1}
        for color in CardColor
    ],
)

uimi = Location(
    "Uimi",
    LocationType.SPECIAL_EVENT,
    1,
    action_resources_to_location(
        "Uimi", [ResourceType.TWIG], 3, {ResourceType.TWIG: 2}
    ),
    action_on_finish=action_points_for_resources_event_location(
        [ResourceType.TWIG], 2, location_name="Uimi"
    ),
    requirements=[
        {
            "kind": RequirementKind.REQUIRED_CARDS_IN_CITY,
            "cards": ["Uitkijkpost", "Mijnwerker mol"],
        },
        {
            "kind": RequirementKind.HAS_RESOURCE_TYPE,
            "resource": ResourceType.TWIG,
            "amount": 1,
        },
    ],
)

wipo = Location(
    "Wipo",
    LocationType.SPECIAL_EVENT,
    1,
    action_points_for_given_resources(max_nr_resources=3, points_per_resource=2),
    requirements=[
        {
            "kind": RequirementKind.REQUIRED_CARDS_IN_CITY,
            "cards": ["Winkelier", "Postkantoor"],
        },
        {"kind": RequirementKind.HAS_ANY_RESOURCE},
    ],
)


# Special events should not be added to init_locations, but to a separate list
special_events.extend(
    [
        behe,
        beki,
        dopo,
        gebo,
        heza,
        hiru,
        hoka,
        klzw,
        leun,
        mawi,
        moke,
        reko,
        sckl,
        twve,
        uimi,
        wipo,
    ]
)


# ============================================
# HAVEN
# ============================================

haven = Location("Haven", LocationType.HAVEN, 99, action_resources_for_cards())
init_locations.append(haven)

# ============================================
# JOURNEY
# ============================================

journey_2 = Location(
    "Journey_2",
    LocationType.JOURNEY,
    99,
    action_discard_cards_from_hand(2),
    permanent_workers=True,
    points=2,
)
journey_3 = Location(
    "Journey_3",
    LocationType.JOURNEY,
    1,
    action_discard_cards_from_hand(3),
    permanent_workers=True,
    points=3,
)
journey_4 = Location(
    "Journey_4",
    LocationType.JOURNEY,
    1,
    action_discard_cards_from_hand(4),
    permanent_workers=True,
    points=4,
)
journey_5 = Location(
    "Journey_5",
    LocationType.JOURNEY,
    1,
    action_discard_cards_from_hand(5),
    permanent_workers=True,
    points=5,
)

init_locations.extend([journey_2, journey_3, journey_4, journey_5])
