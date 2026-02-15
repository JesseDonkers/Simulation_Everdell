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
        self.category = category  # e.g., "cards", "token", "resources"
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
            choice_r = player.decide(game_state, "resource", self.resources)
            player.resources_add(choice_r, 1)


class action_give_away_resources_gain_points(Action):
    def __init__(self, max_nr_resources, resource_type, points_per_resource):
        self.max_nr_resources = max_nr_resources
        self.resource_type = resource_type
        self.points_per_resource = points_per_resource
    
    def execute_action(self, player: "Player", game_state=None):        
        options = [self.max_nr_resources, self.resource_type]
        other_player: "Player"
        nr_give_away = player.decide(
                        game_state, "nr_resources_to_give_away", options)
        other_player = player.decide(
                        game_state, "player_to_receive_resources", None)

        for _ in range(nr_give_away):
            player.resources_remove(self.resource_type, 1)
            player.points["token"] += self.points_per_resource
            other_player.resources_add(self.resource_type, 1)


# class action_spend_resource(Action):
#     def __init__(self, resource_type, amount):
#         self.resource_type = resource_type
#         self.amount = amount
    
#     def execute_action(self, player: "Player", game_state=None):
#         player.resources[self.resource_type] = 
#               max(0, player.resources[self.resource_type] - self.amount)


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
            card = player.decide(game_state, "card", meadow.cards)
            listofcards.append(card)

        meadow.draw_cards(listofcards, deck, discardpile)
        player.cards_add(listofcards, "hand")


# # To do: finish the function below
# class action_add_destination_card(Action):
#     def __init__(self):
#         return self
    
#     def execute_action(self, player: "Player", game_state=None):
#         return self

# # To do: finish the function below
# class action_remove_card_from_city(Action):
#     def __init__(self):
#         return self
    
#     def execute_action(self, player: "Player", game_state=None):
#         # To do: if card.color = red, also remove from locations
#         return self
    


# ============================================
# COMPOSITE ACTIONS
# ============================================

class CompositeAction(Action):
    def __init__(self, listofactions):
        self.actions = listofactions
    
    def execute_action(self, player: "Player", game_state=None):
        for action in self.actions:
            action.execute_action(player, game_state)
            