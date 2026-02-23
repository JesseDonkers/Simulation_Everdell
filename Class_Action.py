from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Class_Player import Player
    from Class_Deck import Deck
    from Class_DiscardPile import DiscardPile
    from Class_Meadow import Meadow


# ============================================
# BASE ACTION CLASS
# ============================================

class Action(ABC):
    def execute(self, game_state=None):
        """
        Template method: Gets the current player from game_state, 
        then calls execute_action for subclasses to implement.
        """
        player = game_state["current_player"]
        self.execute_action(player, game_state)
    
    @abstractmethod
    def execute_action(self, player: "Player", game_state=None):
        """
        Subclasses override this method.
        Player is automatically extracted from game_state.
        """
        pass


# ============================================
# SIMPLE ACTIONS
# ============================================


class action_gain_points(Action):
    def __init__(self, category, points):
        self.category = category
        self.points = points
    
    def execute_action(self, player: "Player", game_state=None):
        player.points[self.category] += self.points


class action_gain_resource(Action):
    def __init__(self, resource_type, amount):
        self.resource_type = resource_type
        self.amount = amount
    
    def execute_action(self, player: "Player", game_state=None):
        player.resources[self.resource_type] += self.amount


class action_gain_resource_per_other_card(Action):
    def __init__(self, cardname, resource_type, amount):
        self.cardname = cardname
        self.resource_type = resource_type
        self.amount = amount
    
    def execute_action(self, player: "Player", game_state=None):
        for c in player.hand:
            if c.name == self.cardname:
                player.resources[self.resource_type] += self.amount            


class action_gain_resource_if_other_card(Action):
    def __init__(self, cardname, resource_type, amount):
        self.cardname = cardname
        self.resource_type = resource_type
        self.amount = amount
    
    def execute_action(self, player: "Player", game_state=None):
        if any(card.name == self.cardname for card in player.hand):
            player.resources[self.resource_type] += self.amount


class action_gain_resources_by_choice(Action):
    def __init__(self, resources, nr_resources):
        self.resources = resources
        self.nr_resources = nr_resources
    
    def execute_action(self, player: "Player", game_state=None):
        for _ in range(self.nr_resources):
            choice = player.decide(game_state, "resource_new", self.resources)
            player.resources_add(choice, 1)


class action_gain_resources_building_costs_discard(Action):
    def __init__(self, critter=False, construction=False):
        self.critter = critter
        self.construction = construction
    
    def execute_action(self, player: "Player", game_state=None):
        critter_construction = [self.critter, self.construction]
        card = player.decide(game_state, "card_discard", critter_construction)
        resources = card.requirements
        for resource, amount in resources.items():
            player.resources_add(resource, amount)

        card.action_on_discard.execute(game_state)


class action_points_for_given_resources(Action):
    """
    Action that handles two patterns:

    - Fixed choose type
        player chooses which resources to give, fixed points
        (nr_resources=2, points=4)

    - Max fixed type
        Player chooses how many to give (up to max), resource type fixed, and
        points per resource
        (max_nr_resources=2, resource_type='berry', points_per_resource=2)
    """
    def __init__(self, nr_resources=None, points=None, max_nr_resources=None, 
                 resource_type=None, points_per_resource=None):
        if nr_resources is not None and points is not None:
            self.mode = "fixed_choose_types"
            self.nr_resources = nr_resources
            self.points = points
        elif (max_nr_resources is not None and resource_type is not None and
              points_per_resource is not None):
            self.mode = "max_fixed_type"
            self.max_nr_resources = max_nr_resources
            self.resource_type = resource_type
            self.points_per_resource = points_per_resource
        else:
            raise ValueError(
                "Invalid arguments for action_points_for_given_resources")

    def execute_action(self, player: "Player", game_state=None):
        other_player = player.decide(
                        game_state, "player_to_receive_resources", None)

        if self.mode == "fixed_choose_types":
            resources = player.decide(
                        game_state, "resource_give_away", self.nr_resources)
            for resource_type in resources:
                player.resources_remove(resource_type, 1)
                other_player.resources_add(resource_type, 1)
            player.points["token"] += self.points

        else:  # max_fixed_type
            nr_and_type = [self.max_nr_resources, self.resource_type]
            nr_give_away = player.decide(
                        game_state, "nr_resources_to_give_away", nr_and_type)

            for _ in range(nr_give_away):
                player.resources_remove(self.resource_type, 1)
                player.points["token"] += self.points_per_resource
                other_player.resources_add(self.resource_type, 1)


class action_draw_cards_from_deck(Action):
    def __init__(self, nrCards):
        self.nrCards = nrCards
    
    def execute_action(self, player: "Player", game_state=None):
        deck: "Deck" = game_state["deck"]
        discardpile: "DiscardPile" = game_state["discardpile"]
        spaces_hand = player.cards_get_open_spaces("hand")
        nr_draw = min(self.nrCards, spaces_hand)
        listofcards = deck.draw_cards(nr_draw, discardpile)
        player.cards_add(listofcards, "hand")


class action_draw_cards_from_meadow(Action):
    def __init__(self, nrCards):
        self.nrCards = nrCards
    
    def execute_action(self, player: "Player", game_state=None):
        meadow: "Meadow" = game_state["meadow"]
        deck = game_state["deck"]
        discardpile = game_state["discardpile"]
        spaces_hand = player.cards_get_open_spaces("hand")
        listofcards = []

        for _ in range(min(self.nrCards, spaces_hand)):
            card = player.decide(game_state, "card_new", meadow.cards)
            listofcards.append(card)

        meadow.draw_cards(listofcards, deck, discardpile)
        player.cards_add(listofcards, "hand")


class action_add_destination_card_as_location(Action):
    def __init__(self, name, type, open, 
                 maxworkers, action, permanent_workers=False):
        self.name = name
        self.type = type
        self.open = open
        self.maxworkers = maxworkers
        self.action = action
        self.permanent_workers = permanent_workers
    
    def execute_action(self, player: "Player", game_state=None):
        from Class_Location import Location
        locations = game_state["locations"]
        dest_card = Location(
            self.name, self.type, self.open, self.maxworkers,
            self.action, permanent_workers=self.permanent_workers)
        locations.append(dest_card)


class action_add_destination_if_card_present(Action):
    """
    Add a destination_card location only if a specified card is present in the
    current player's city.
    """
    def __init__(self, name, type, open, maxworkers, action, 
                 check_card_name, permanent_workers=False):
        self.name = name
        self.type = type
        self.open = open
        self.maxworkers = maxworkers
        self.action = action
        self.check_card_name = check_card_name
        self.permanent_workers = permanent_workers

    def execute_action(self, player: "Player", game_state=None):
        from Class_Location import Location
        locations = game_state["locations"]

        # Check if the specified card is in the player's city
        card_in_city = any(
                    card.name == self.check_card_name for card in player.city)

        if card_in_city:
            dest_card = Location(
                self.name, self.type, self.open, self.maxworkers,
                self.action, permanent_workers=self.permanent_workers)
            locations.append(dest_card)


class action_remove_destination(Action):
    """
    Remove a destination location by name.
    Typically used when a card that created the location is discarded.
    """
    def __init__(self, location_name):
        self.location_name = location_name

    def execute_action(self, player: "Player", game_state=None):
        locations = game_state["locations"]
        targets = [loc for loc in locations if loc.name == self.location_name]

        temp_loc = next(l for l in locations if l.type == "temporary")
        perm_loc = next(l for l in locations if l.type == "permanent")

        for loc in targets:
            # Choose where to move workers depending on the source location
            if getattr(loc, "permanent_workers", False):
                safe_loc = perm_loc
            else:
                safe_loc = temp_loc

            # Copy items to avoid mutation during iteration
            for p, count in list(loc.workers.items()):
                for _ in range(count):
                    loc.remove_worker(p)
                    safe_loc.add_worker(p)

        # Remove the specified location(s)
        locations[:] = [l for l in locations if l.name != self.location_name]


class action_remove_card_from_city(Action):
    def __init__(self, card_name):
        self.card_name = card_name
    
    def execute_action(self, player: "Player", game_state=None):
        card = next(c for c in player.city if c.name == self.card_name)
        player.cards_remove([card], "city")
        discard_pile: "DiscardPile" = game_state["discardpile"]
        discard_pile.add_to_discardpile([card])


class action_location_copy_action(Action):
    def __init__(self, possible_locations):
        self.possible_locations = possible_locations
    
    def execute_action(self, player: "Player", game_state=None):
        locations = game_state["locations"]
        locations_of_type = [l for l in locations 
                             if l.type in self.possible_locations]
        loc = player.decide(game_state, "location", locations_of_type)
        loc.action.execute(game_state)


# ============================================
# COMPOSITE ACTIONS
# ============================================

class CompositeAction(Action):
    def __init__(self, listofactions):
        self.actions = listofactions
    
    def execute_action(self, player: "Player", game_state=None):
        for action in self.actions:
            action.execute_action(player, game_state)
            