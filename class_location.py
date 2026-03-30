from typing import TYPE_CHECKING, Any

import class_action

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
        requirements: Any = None
    ):
        self.name = name
        self.location_type = location_type # For example basic, journey, haven
        self.is_open = is_open # Attribute for destination cards
        self.maxworkers = maxworkers
        self.action_on_place_worker = action_on_place_worker
        self.action_on_finish = action_on_finish
        self.workers: dict["Player", int] = {}
        self.resources = dict(twig=0, resin=0, pebble=0, berry=0)
        self.permanent_workers = permanent_workers
        self.owner = owner  # Player that owns this destination location
        self.points = points
        self.requirements = requirements
        
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
permanent = Location(
    "Permanent", "permanent", 0, None, permanent_workers=True
)

init_locations.append(temp)
init_locations.append(permanent)


# ============================================
# BASIC
# ============================================

twigs = Location("Three_twigs", "basic", 1,
           class_action.action_resource_general("twig", 3))
resins = Location("Two_resins", "basic", 1,
            class_action.action_resource_general("resin", 2))
pebble = Location("One_pebble", "basic", 1,
            class_action.action_resource_general("pebble", 1))
berry = Location("One_berry", "basic", 99,
           class_action.action_resource_general("berry", 1))

twigs_card = Location("Twigs_point", "basic", 99,
               class_action.CompositeAction(
               [class_action.action_resource_general("twig", 2), 
               class_action.action_cards_from_deck_to_hand(1)]))
resin_card = Location("Resins_point", "basic", 99,
               class_action.CompositeAction(
               [class_action.action_resource_general("resin", 1), 
               class_action.action_cards_from_deck_to_hand(1)]))
cards_point = Location("Cards_point", "basic", 99,
               class_action.CompositeAction(
               [class_action.action_points_general("token", 1),
               class_action.action_cards_from_deck_to_hand(2)]))
berry_card = Location("Berry_card", "basic", 1,
               class_action.CompositeAction(
               [class_action.action_resource_general("berry", 1),
               class_action.action_cards_from_deck_to_hand(1)]))

init_locations.extend([twigs, resins, pebble, berry])
init_locations.extend([twigs_card, resin_card, cards_point, berry_card])


# ============================================
# FOREST
# ============================================

# Add constraint for number of workers per player = max 1

cards_for_resources = None # To do
card_for_cards = None # To do
card_from_meadow = None # To do
copy_basic_location = None # To do
berries_card = None # To do
twig_resin_berry = None # To do
resins_twig = None # To do
cards_resource = None # To do
two_resources = None # To do
cards_pebble = None # To do
berries = None # To do

# To do: should not be added to init_locations, but seperate forest_locations list


# ============================================
# BASIC EVENTS
# ============================================
monument = Location(
    "Monument",
    "event",
    1,
    None,
    action_on_finish=class_action.action_points_general("event", 3),
    requirements={"kind": "min_color_cards", "color": "blue", "count": 3},
)
tour = Location(
    "Tour",
    "event",
    1,
    None,
    action_on_finish=class_action.action_points_general("event", 3),
    requirements={"kind": "min_color_cards", "color": "red", "count": 3},
)
festival = Location(
    "Festival",
    "event",
    1,
    None,
    action_on_finish=class_action.action_points_general("event", 3),
    requirements={"kind": "min_color_cards", "color": "green", "count": 4},
)
expedition = Location(
    "Expedition",
    "event",
    1,
    None,
    action_on_finish=class_action.action_points_general("event", 3),
    requirements={"kind": "min_color_cards", "color": "tan", "count": 3},
)

init_locations.extend([monument, tour, festival, expedition])


# ============================================
# SPECIAL EVENTS
# ============================================

special_events = []

hiru = None # To do

heza = Location(
    "Heza",
    "event",
    1,
    class_action.action_resources_to_location("Heza", ["berry"], 3),

    action_on_finish=class_action.actions_points_for_resources_event_location(
        ["berry"], 2, location_name="Heza"),
    
    requirements=[{"kind": "required_cards_in_city", 
                   "cards": ["Herberg", "Zanger"]},
                  {"kind": "can_add_location_resource", 
                   "resource": "berry", "amount": 1}])

sckl = None # To do
reko = None # To do
dopo = None # To do
gebo = None # To do
behe = None # To do
klzw = None # To do
moke = None # To do
mawi = None # To do
wipo = None # To do
twve = None # To do
beki = None # To do
uimi = None # To do
hoka = None # To do
leun = None # To do

# Special events should not be added to init_locations, but to a separate list
special_events.extend([heza, heza, heza, heza]) # To do: add all special events


# ============================================
# HAVEN
# ============================================

haven = Location("Haven", "haven", 99,
                 class_action.action_resources_for_cards())
init_locations.append(haven)

# ============================================
# JOURNEY
# ============================================

journey_2 = Location("Journey_2", "journey", 99,
    class_action.action_discard_cards_from_hand(2),
    permanent_workers=True, points=2)
journey_3 = Location("Journey_3", "journey", 1,
    class_action.action_discard_cards_from_hand(3),
    permanent_workers=True, points=3)
journey_4 = Location("Journey_4", "journey", 1,
    class_action.action_discard_cards_from_hand(4),
    permanent_workers=True, points=4)
journey_5 = Location("Journey_5", "journey", 1,
    class_action.action_discard_cards_from_hand(5),
    permanent_workers=True, points=5)

init_locations.extend([journey_2, journey_3, journey_4, journey_5])
