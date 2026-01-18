from abc import ABC, abstractmethod


# ============================================
# BASE ACTION CLASS
# ============================================

class Action(ABC):
    def execute(self, game_state=None):
        """
        Template method: Gets the current player from game_state, 
        then calls execute_action for subclasses to implement.
        """
        player = game_state['current_player']
        self.execute_action(player, game_state)
    
    @abstractmethod
    def execute_action(self, player, game_state=None):
        """
        Subclasses override this method. Player is automatically extracted from game_state.
        """
        pass


# ============================================
# SIMPLE ACTIONS
# ============================================

class action_gain_resource(Action):
    def __init__(self, resource_type, amount):
        self.resource_type = resource_type  # 'twig', 'resin', 'pebble', 'berry'
        self.amount = amount
    
    def execute_action(self, player, game_state=None):
        player.resources[self.resource_type] += self.amount


class action_spend_resource(Action):
    def __init__(self, resource_type, amount):
        self.resource_type = resource_type
        self.amount = amount
    
    def execute_action(self, player, game_state=None):
        player.resources[self.resource_type] = max(0, player.resources[self.resource_type] - self.amount)


class action_draw_cards_from_deck(Action):
    def __init__(self, nrCards):
        self.nrCards = nrCards
    
    def execute_action(self, player, game_state=None):
        deck = game_state['deck']
        discardpile = game_state['discardpile']
        for _ in range(self.nrCards):
            listofcards = deck.draw_cards(self.nrCards, discardpile)
            player.cards_add(listofcards, 'hand')
            


############################################################################################
# Hierboven gebleven
#############################################################################################

# class PlayCardAction(Action):
#     """Play a card for free (skip cost check)."""
#     def __init__(self, card):
#         self.card = card
    
#     def execute(self, player, game_state=None):
#         if self.card in player.hand:
#             player.hand.remove(self.card)
#             player.city.append(self.card)


# class GainPointTokenAction(Action):
#     """Gain point tokens."""
#     def __init__(self, count):
#         self.count = count
    
#     def execute(self, player, game_state=None):
#         player.points['tokens'] = player.points.get('tokens', 0) + self.count


# class AddWorkerAction(Action):
#     """Add a worker back to player's pool."""
#     def __init__(self, count):
#         self.count = count
    
#     def execute(self, player, game_state=None):
#         player.workers += self.count


# class ActivateLocationAction(Action):
#     """Activate another location's actions."""
#     def __init__(self, location):
#         self.location = location
    
#     def execute(self, player, game_state=None):
#         if self.location.actions:
#             for action in self.location.actions:
#                 action.execute(player, game_state)


# # ============================================
# # COMPOSITE ACTIONS
# # ============================================

# class CompositeAction(Action):
#     """Combine multiple actions to execute in sequence."""
#     def __init__(self, *actions):
#         self.actions = actions
    
#     def execute(self, player, game_state=None):
#         for action in self.actions:
#             action.execute(player, game_state)


# # ============================================
# # CONDITIONAL ACTIONS
# # ============================================

# class ConditionalAction(Action):
#     """Execute an action only if a condition is met."""
#     def __init__(self, condition_func, action):
#         """
#         :param condition_func: Function that takes (player, game_state) and returns True/False
#         :param action: Action to execute if condition is True
#         """
#         self.condition_func = condition_func
#         self.action = action
    
#     def execute(self, player, game_state=None):
#         if self.condition_func(player, game_state):
#             self.action.execute(player, game_state)


# class ConditionalMultiAction(Action):
#     """Execute different actions based on conditions."""
#     def __init__(self):
#         self.conditions = []  # List of (condition_func, action) tuples
    
#     def add_condition(self, condition_func, action):
#         """Add a condition and its associated action."""
#         self.conditions.append((condition_func, action))
    
#     def execute(self, player, game_state=None):
#         for condition_func, action in self.conditions:
#             if condition_func(player, game_state):
#                 action.execute(player, game_state)
#                 return  # Execute first matching condition only


# # ============================================
# # COUNTING-BASED ACTIONS
# # ============================================

# class GainResourcePerCountAction(Action):
#     """Gain resources based on count of cards/items."""
#     def __init__(self, resource_type, count_func):
#         """
#         :param resource_type: Resource to gain
#         :param count_func: Function that takes (player, game_state) and returns count
#         """
#         self.resource_type = resource_type
#         self.count_func = count_func
    
#     def execute(self, player, game_state=None):
#         count = self.count_func(player, game_state)
#         player.resources[self.resource_type] += count


# class CountCardsAction(Action):
#     """Count cards matching a condition and add as points/resources."""
#     def __init__(self, resource_type, filter_func, amount_per_card=1):
#         """
#         :param resource_type: What to gain ('points', 'twig', etc.)
#         :param filter_func: Function to filter cards (e.g., lambda card: card.color == 'green')
#         :param amount_per_card: Amount to gain per matching card
#         """
#         self.resource_type = resource_type
#         self.filter_func = filter_func
#         self.amount_per_card = amount_per_card
    
#     def execute(self, player, game_state=None):
#         count = sum(1 for card in player.city if self.filter_func(card))
#         if self.resource_type == 'points':
#             player.points['cards'] = player.points.get('cards', 0) + (count * self.amount_per_card)
#         else:
#             player.resources[self.resource_type] += (count * self.amount_per_card)


# # ============================================
# # CUSTOM ACTIONS
# # ============================================

# class CustomAction(Action):
#     """Execute a custom function as an action."""
#     def __init__(self, func):
#         """
#         :param func: Function that takes (player, game_state) and performs the action
#         """
#         self.func = func
    
#     def execute(self, player, game_state=None):
#         self.func(player, game_state)


# # ============================================
# # HELPER FUNCTIONS FOR COMMON CONDITIONS
# # ============================================

# def has_card_with_property(property_name, property_value):
#     """Return a condition function that checks if player has a card with a property."""
#     def condition(player, game_state=None):
#         return any(getattr(card, property_name, None) == property_value for card in player.city)
#     return condition


# def has_resource_count(resource_type, min_count):
#     """Return a condition function that checks if player has minimum resources."""
#     def condition(player, game_state=None):
#         return player.resources.get(resource_type, 0) >= min_count
#     return condition


# def count_cards_with_property(property_name, property_value):
#     """Return a counting function that counts cards with a property."""
#     def count_func(player, game_state=None):
#         return sum(1 for card in player.city if getattr(card, property_name, None) == property_value)
#     return count_func
