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
    def __init__(self, otherplayer, resourcesequence):
        self.otherplayer = otherplayer
        self.resourcesequence = resourcesequence
    
    def __str__(self):
        a = str("Other player index: " + str(self.otherplayer.index))
        b = str("Resource sequence: " + str(self.resourcesequence))
        return a + "\n" + b


# ============================================
# CLASS PER STRATEGY
# ============================================

class Strategy_random(Strategy):
    def __init__(self, player, game_state):
        super().__init__(get_random_other_player(player, game_state), 
                        get_random_resource())

