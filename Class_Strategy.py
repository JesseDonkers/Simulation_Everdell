import random


# ============================================
# FUNCTIONS
# ============================================

def get_random_other_player(player, game_state):
    players = game_state["players"]
    other_players = [p for p in players if p != player]
    return random.choice(other_players)

def get_random_resource():
    resources = ["twig", "resin", "pebble", "berry"]
    random.shuffle(resources)
    return resources


# ============================================
# GENERAL CLASS
# ============================================

class Strategy:
    def __init__(self, own_player_index, other_player_index, otherplayer, resourcesequence):
        self.own_player_index = own_player_index
        self.other_player_index = other_player_index
        self.otherplayer = otherplayer
        self.resourcesequence = resourcesequence
    
    def __str__(self):
        a = str("Own player index: " + str(self.own_player_index))
        b = str("Other player index: " + str(self.other_player_index))
        c = str("Resource sequence: " + str(self.resourcesequence))
        return a + "\n" + b + "\n" + c


# ============================================
# CLASS PER STRATEGY
# ============================================

class Strategy_random(Strategy):
    def __init__(self, player, game_state):
        other_player = get_random_other_player(player, game_state)
        own_player_index = game_state["players"].index(player)
        other_player_index = game_state["players"].index(other_player)
        super().__init__(own_player_index,
                        other_player_index,
                        other_player, 
                        get_random_resource())

