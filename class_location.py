from typing import TYPE_CHECKING, Any

from actions.base import CompositeAction
from actions.cards import (
    action_cards_from_deck_to_hand,
    action_discard_cards_from_city,
    action_discard_cards_from_hand,
    action_discard_cards_for_deck_cards,
    action_play_two_meadow_cards_with_discount,
    action_reactivate_all_green_cards,
)
from actions.locations import action_retake_worker
from actions.points import (
    action_points_for_given_resources,
    action_points_for_city_assets,
    action_points_for_resources_event_location,
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

if TYPE_CHECKING:
    from class_player import Player


class Location:
    def __init__(
        self,
        name: str,
        location_type: str,
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
        self.name = name
        self.location_type = location_type  # For example basic, journey, haven
        self.is_open = is_open  # Attribute for destination cards
        self.maxworkers = maxworkers
        self.action_on_place_worker = action_on_place_worker
        self.action_on_finish = action_on_finish
        self.workers: dict["Player", int] = {}
        self.resources = dict(twig=0, resin=0, pebble=0, berry=0)
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
    def resources_add(self, resource, amount):
        self.resources[resource] += amount
        return self.resources

    # Function to remove resources from a specific category
    def resources_remove(self, resource, amount):
        self.resources[resource] -= amount
        return self.resources


init_locations = []


# ============================================
# TEMPORARY AND PERMANENT
# ============================================

# A temporary location is added which can be used when a location is removed
# and already placed workers need to be stored somewhere temporarily.
temp = Location("Temporary", "temporary", 0, None)

# A permanent location is added which can be used when a permanent location
# is removed and already placed workers need to be stored somewhere.
permanent = Location("Permanent", "permanent", 0, None, permanent_workers=True)

init_locations.append(temp)
init_locations.append(permanent)


# ============================================
# BASIC
# ============================================

twigs = Location("Three_twigs", "basic", 1, action_resource_general("twig", 3))
resins = Location("Two_resins", "basic", 1, action_resource_general("resin", 2))
pebble = Location("One_pebble", "basic", 1, action_resource_general("pebble", 1))
berry = Location("One_berry", "basic", 99, action_resource_general("berry", 1))

twigs_card = Location(
    "Twigs_Card",
    "basic",
    99,
    CompositeAction(
        [
            action_resource_general("twig", 2),
            action_cards_from_deck_to_hand(1),
        ]
    ),
)
resin_card = Location(
    "Resin_Card",
    "basic",
    99,
    CompositeAction(
        [
            action_resource_general("resin", 1),
            action_cards_from_deck_to_hand(1),
        ]
    ),
)
cards_point = Location(
    "Cards_Point",
    "basic",
    99,
    CompositeAction(
        [
            action_points_general("token", 1),
            action_cards_from_deck_to_hand(2),
        ]
    ),
)
berry_card = Location(
    "Berry_Card",
    "basic",
    1,
    CompositeAction(
        [
            action_resource_general("berry", 1),
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
    "forest",
    1,
    action_resources_for_cards(max_discard=3, cards_per_resource=1),
    requirements={"kind": "has_hand_cards", "amount": 1},
)
card_for_cards = Location(
    "Cards_For_Cards",
    "forest",
    1,
    action_discard_cards_for_deck_cards(),
    requirements={"kind": "has_hand_cards", "amount": 1},
)
card_from_meadow = Location(
    "Card_From_Meadow",
    "forest",
    1,
    action_play_two_meadow_cards_with_discount(),
    requirements=[
        {"kind": "has_city_space"},
        {"kind": "has_playable_meadow_card", "discount": 1},
    ],
)
copy_basic_location = Location(
    "Copy_Basic",
    "forest",
    1,
    CompositeAction(
        [
            action_location_copy_action(["basic"]),
            action_cards_from_deck_to_hand(1),
        ]
    ),
)
two_resources = Location(
    "Two_resources",
    "forest",
    1,
    action_resources_by_choice(["twig", "resin", "pebble", "berry"], 2),
)
cards_resource = Location(
    "Cards_Resource",
    "forest",
    1,
    CompositeAction(
        [
            action_resources_by_choice(["twig", "resin", "pebble", "berry"], 1),
            action_cards_from_deck_to_hand(2),
        ]
    ),
)
twig_resin_berry = Location(
    "Twig_Resin_Berry",
    "forest",
    1,
    CompositeAction(
        [
            action_resource_general("twig", 1),
            action_resource_general("resin", 1),
            action_resource_general("berry", 1),
        ]
    ),
)
cards_pebble = Location(
    "Cards_Pebble",
    "forest",
    1,
    CompositeAction(
        [
            action_resource_general("pebble", 1),
            action_cards_from_deck_to_hand(3),
        ]
    ),
)
berries_card = Location(
    "Berries_Card",
    "forest",
    1,
    CompositeAction(
        [
            action_resource_general("berry", 2),
            action_cards_from_deck_to_hand(1),
        ]
    ),
)
resins_twig = Location(
    "Resins_Twig",
    "forest",
    1,
    CompositeAction(
        [
            action_resource_general("resin", 2),
            action_resource_general("twig", 1),
        ]
    ),
)
berries = Location("Three_berries", "forest", 1, action_resource_general("berry", 3))


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
    "basic_event",
    1,
    None,
    action_on_finish=action_points_general("event", 3),
    requirements={"kind": "min_color_cards", "color": "blue", "count": 3},
)
tour = Location(
    "Tour",
    "basic_event",
    1,
    None,
    action_on_finish=action_points_general("event", 3),
    requirements={"kind": "min_color_cards", "color": "red", "count": 3},
)
festival = Location(
    "Festival",
    "basic_event",
    1,
    None,
    action_on_finish=action_points_general("event", 3),
    requirements={"kind": "min_color_cards", "color": "green", "count": 4},
)
expedition = Location(
    "Expedition",
    "basic_event",
    1,
    None,
    action_on_finish=action_points_general("event", 3),
    requirements={"kind": "min_color_cards", "color": "tan", "count": 3},
)

init_locations.extend([monument, tour, festival, expedition])


# ============================================
# SPECIAL EVENTS
# ============================================

special_events = []

hiru = None  # TODO

heza = Location(
    "Heza",
    "special_event",
    1,
    action_resources_to_location("Heza", ["berry"], 3, {"berry": 2}),
    action_on_finish=action_points_for_resources_event_location(
        ["berry"], 2, location_name="Heza"
    ),
    requirements=[
        {"kind": "required_cards_in_city", "cards": ["Herberg", "Zanger"]},
        {"kind": "has_resource_type", "resource": "berry", "amount": 1},
    ],
)

sckl = Location(
    "Sckl",
    "special_event",
    1,
    action_retake_worker(),
    action_on_finish=action_points_general("event", 4),
    requirements=[
        {
            "kind": "required_cards_in_city",
            "cards": ["Schoonmaker", "Klokkentoren"],
        },
        {"kind": "has_placed_worker"},
    ],
)

reko = Location(
    "Reko",
    "special_event",
    1,
    action_reactivate_all_green_cards(),
    action_on_finish=action_points_general("event", 3),
    requirements=[
        {
            "kind": "required_cards_in_city",
            "cards": ["Rechter", "Koningin"],
        },
    ],
)

dopo = Location(
    "Dopo",
    "special_event",
    1,
    None,
    action_on_finish=action_points_for_city_assets(
        "card_pairs", 3, paired_card_names=("Man", "Vrouw")
    ),
    requirements={
        "kind": "required_cards_in_city",
        "cards": ["Dokter", "Postduif"],
    },
)
gebo = None  # TODO
behe = Location(
    "Behe",
    "special_event",
    1,
    None,
    action_on_finish=action_points_for_city_assets(
        "destination_workers", 3, card_name="Begraafplaats"
    ),
    requirements={
        "kind": "required_cards_in_city",
        "cards": ["Begraafplaats", "Herder"],
    },
)
klzw = Location(
    "Klzw",
    "special_event",
    1,
    None,
    action_on_finish=action_points_for_city_assets(
        "destination_workers", 3, card_name="Klooster"
    ),
    requirements={
        "kind": "required_cards_in_city",
        "cards": ["Klooster", "Zwerver"],
    },
)
moke = Location(
    "Moke",
    "special_event",
    1,
    None,
    action_on_finish=action_points_for_city_assets(
        "stored_cards", 3, card_name="Kerker"
    ),
    requirements={
        "kind": "required_cards_in_city",
        "cards": ["Monnik", "Kerker"],
    },
)
mawi = Location(
    "Mawi",
    "special_event",
    1,
    action_resources_to_location(
        "Mawi",
        ["berry", "twig", "resin", "pebble"],
        3,
        points_per_resource={"berry": 1, "twig": 1, "resin": 2, "pebble": 2},
    ),
    action_on_finish=action_points_for_resources_event_location(
        ["berry", "twig", "resin", "pebble"],
        {"berry": 1, "twig": 1, "resin": 2, "pebble": 2},
        location_name="Mawi",
    ),
    requirements=[
        {"kind": "required_cards_in_city", "cards": ["Marskramer", "Winkel"]},
        {"kind": "has_any_resource"},
    ],
)

wipo = Location(
    "Wipo",
    "special_event",
    1,
    action_points_for_given_resources(max_nr_resources=3, points_per_resource=2),
    requirements=[
        {"kind": "required_cards_in_city", "cards": ["Winkelier", "Postkantoor"]},
        {"kind": "has_any_resource"},
    ],
)

twve = Location(
    "Twve",
    "special_event",
    1,
    None,
    action_on_finish=action_points_general("event", 9),
    requirements=[
        {"kind": "min_color_cards", "color": color, "count": 1}
        for color in ("tan", "red", "green", "blue", "purple")
    ],
)
beki = Location(
    "Beki",
    "special_event",
    1,
    CompositeAction(
        [
            action_resource_general("berry", -2),
            action_discard_cards_from_city(2),
        ]
    ),
    action_on_finish=action_points_general("event", 6),
    requirements=[
        {
            "kind": "required_cards_in_city",
            "cards": ["Begrafenisondernemer", "Kikkerkapitein"],
        },
        {"kind": "has_city_cards", "amount": 2},
        {"kind": "has_resource_type", "resource": "berry", "amount": 2},
    ],
)

uimi = Location(
    "Uimi",
    "special_event",
    1,
    action_resources_to_location("Uimi", ["twig"], 3, {"twig": 2}),
    action_on_finish=action_points_for_resources_event_location(
        ["twig"], 2, location_name="Uimi"
    ),
    requirements=[
        {"kind": "required_cards_in_city", "cards": ["Uitkijkpost", "Mijnwerker mol"]},
        {"kind": "has_resource_type", "resource": "twig", "amount": 1},
    ],
)

hoka = Location(
    "Hoka",
    "special_event",
    1,
    CompositeAction(
        [
            action_cards_from_deck_to_hand(1),
            action_resources_by_choice_for_card_tokens(
                "Kapel", ["twig", "resin", "pebble", "berry"]
            ),
        ]
    ),
    action_on_finish=action_points_for_tokens_on_card(
        "Kapel", points_per_token=2, category="event"
    ),
    requirements={
        "kind": "required_cards_in_city",
        "cards": ["Houtsnijder", "Kapel"],
    },
)
leun = None  # TODO

# Special events should not be added to init_locations, but to a separate list
special_events.extend(
    [heza, sckl, reko, dopo, behe, klzw, moke, mawi, wipo, twve, beki, uimi, hoka]
)
# TODO: add all special events


# ============================================
# HAVEN
# ============================================

haven = Location("Haven", "haven", 99, action_resources_for_cards())
init_locations.append(haven)

# ============================================
# JOURNEY
# ============================================

journey_2 = Location(
    "Journey_2",
    "journey",
    99,
    action_discard_cards_from_hand(2),
    permanent_workers=True,
    points=2,
)
journey_3 = Location(
    "Journey_3",
    "journey",
    1,
    action_discard_cards_from_hand(3),
    permanent_workers=True,
    points=3,
)
journey_4 = Location(
    "Journey_4",
    "journey",
    1,
    action_discard_cards_from_hand(4),
    permanent_workers=True,
    points=4,
)
journey_5 = Location(
    "Journey_5",
    "journey",
    1,
    action_discard_cards_from_hand(5),
    permanent_workers=True,
    points=5,
)

init_locations.extend([journey_2, journey_3, journey_4, journey_5])
