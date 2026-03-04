from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Class_Player import Player
    from Class_Deck import Deck
    from Class_DiscardPile import DiscardPile
    from Class_Meadow import Meadow
    from Class_Location import Location
    from Class_Card import Card


# ============================================
# HELPER FUNCTIONS: GET POSSIBILITIES
#   - Cards to play
#   - Locations to place worker
#   - Moves to make)
# ============================================

def get_possible_cards(game_state, max_points, pay):
        player = game_state["current_player"]
        meadow = game_state["meadow"]
        all_cards = player.hand + meadow.cards
        possible_cards = []

        # Maximum city size
        if player.cards_get_open_spaces("city") == 0:
            return possible_cards
        
        else:
            for card in all_cards:

                # Cards are only allowed when not exceeding the max points
                if card.points > max_points:
                    continue

                # Player may only have one specific copy of any unique card
                if card.unique:
                    if any(c.name == card.name for c in player.city):
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
                    from Class_Card import Critter
                    from Class_Card import Construction
                    
                    constructions = [
                        c for c in player.city if isinstance(c, Construction)]

                    if isinstance(card, Critter):
                        for constr in constructions:
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
# HELPER FUNCTIONS
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
    """
    Sets player.finished to True and evaluates all points. \n
    Returns list of points of all players if all players finished the game.
    """
    player: "Player" = game_state["current_player"]
    players = game_state["players"]
    player.finished = True

    # Card points
    for card in player.city:
        player.points_add("card", card.points)

        # Prosperity points
        if card.color == "purple":
            card.action_on_finish.execute(game_state)


     
    # Journey points
    # To do

    # Event points
    # To do


    # If all players have finished the game, compare sum of points
    if all(p.finished for p in players):
        points = [p.points_total() for p in players]
        return points


# To do: make the following 2 functions into actions


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
# COMPOSITE ACTIONS
# ============================================

class CompositeAction(Action):
    def __init__(self, listofactions):
        self.actions = listofactions
    
    def execute_action(self, player: "Player", game_state=None):
        for action in self.actions:
            action.execute_action(player, game_state)


# ============================================
# ACTIONS REGARDING POINTS
# ============================================

class action_points_general(Action):
    def __init__(self, category, points):
        self.category = category
        self.points = points
    
    def execute_action(self, player: "Player", game_state=None):
        player.points[self.category] += self.points


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


class action_points_for_payed_resources(Action):
    def __init__(self, max_nr_resources=None, resource_type=None, 
                 points_per_resource=None):
        self.max_nr_resources = max_nr_resources
        self.resource_type = resource_type
        self.points_per_resource = points_per_resource

    def execute_action(self, player: "Player", game_state=None):
        nr_and_type = [self.max_nr_resources, self.resource_type]
        nr_give_away = player.decide(
                    game_state, "nr_resources_to_pay", nr_and_type)

        for _ in range(nr_give_away):
            player.resources_remove(self.resource_type, 1)
            player.points["token"] += self.points_per_resource


class actions_points_for_resources_hand(Action):
    def __init__(self, resources, point_per_resource):
        self.resources = resources
        self.point_per_resource = point_per_resource

    def execute_action(self, player: "Player", game_state=None):
        for r in self.resources:
            qty = player.resources.get(r, 0)
            for _ in range(qty):
                player.points_add("prosperity", self.point_per_resource)
    

class actions_points_for_cards(Action):
    def __init__(self, critter_or_construction, unique, points_per_card):
        self.critter_or_construction = critter_or_construction
        self.unique = unique
        self.points_per_card = points_per_card

    def execute_action(self, player: "Player", game_state=None):
        for card in player.city:
            if (card.unique is self.unique and 
                type(card).__name__ == self.critter_or_construction):
                    player.points_add("prosperity", self.points_per_card)


# ============================================
# ACTIONS REGARDING REOURCES
# ============================================

class action_resource_general(Action):
    def __init__(self, resource_type, amount):
        self.resource_type = resource_type
        self.amount = amount
    
    def execute_action(self, player: "Player", game_state=None):
        player.resources[self.resource_type] += self.amount


class action_resource_per_other_card(Action):
    def __init__(self, cardname, resource_type, amount):
        self.cardname = cardname
        self.resource_type = resource_type
        self.amount = amount
    
    def execute_action(self, player: "Player", game_state=None):
        for c in player.hand:
            if c.name == self.cardname:
                player.resources[self.resource_type] += self.amount            


class action_resource_if_other_card(Action):
    def __init__(self, cardname, resource_type, amount):
        self.cardname = cardname
        self.resource_type = resource_type
        self.amount = amount
    
    def execute_action(self, player: "Player", game_state=None):
        if any(card.name == self.cardname for card in player.hand):
            player.resources[self.resource_type] += self.amount


class action_resources_by_choice(Action):
    def __init__(self, resources, nr_resources):
        self.resources = resources
        self.nr_resources = nr_resources
    
    def execute_action(self, player: "Player", game_state=None):
        for _ in range(self.nr_resources):
            choice = player.decide(game_state, "resource_new", self.resources)
            player.resources_add(choice, 1)


class action_resources_building_costs_discard(Action):
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


# ============================================
# ACTIONS REGARDING CARDS
# ============================================

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


class action_remove_card_from_city(Action):
    def __init__(self, card_name):
        self.card_name = card_name
    
    def execute_action(self, player: "Player", game_state=None):
        card = next(c for c in player.city if c.name == self.card_name)
        player.cards_remove([card], "city")
        discard_pile: "DiscardPile" = game_state["discardpile"]
        discard_pile.add_to_discardpile([card])


class action_play_card(Action):
    def __init__(self, max_points=99, pay=True):
        self.max_points = max_points
        self.pay = pay
    
    def execute_action(self, player: "Player", game_state=None):
        meadow: "Meadow" = game_state["meadow"]
        deck = game_state["deck"]
        discardpile = game_state["discardpile"]
        possible_cards = get_possible_cards(
                                        game_state, self.max_points, self.pay)
        
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

            # The player pays for the costs of the card if self.pay == True
            if self.pay:
                card_costs = card.requirements
                for resource, amount in card_costs.items():
                    player.resources_remove(resource, amount)
            
            # Card is added to the player's city and action_on_play is executed
            player.cards_add([card], "city")
            if card.action_on_play:
                card.action_on_play.execute(game_state)        


# ============================================
# ACTIONS REGARDING LOCATIONS
# ============================================

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


class action_location_copy_action(Action):
    def __init__(self, possible_locations):
        self.possible_locations = possible_locations
    
    def execute_action(self, player: "Player", game_state=None):
        locations = game_state["locations"]
        locations_of_type = [l for l in locations 
                             if l.type in self.possible_locations]
        loc = player.decide(game_state, "location", locations_of_type)
        loc.action.execute(game_state)
            