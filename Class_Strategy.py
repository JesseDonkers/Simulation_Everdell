import random


# ============================================
# BASE STRATEGY CLASS
# ============================================

class Strategy():
    def decide(self, game_state, decision_kind, options):
        handler_name = f"choose_{decision_kind}"
        handler = getattr(self, handler_name, None)

        if handler is None:
            raise ValueError(f"Unknown decision type: {decision_kind}")
        return handler(game_state, options)


# ============================================
# CLASS PER STRATEGY
# ============================================

class Strategy_random(Strategy):
    def choose_move(self, game_state, possible_moves):
        return random.choice(possible_moves)

    def choose_card(self, game_state, possible_cards):
        return random.choice(possible_cards)

    def choose_location(self, game_state, possible_locations):
        return random.choice(possible_locations)

    def choose_other_player(self, game_state, _):
        player = game_state["current_player"]
        players = game_state["players"]
        other_players = [p for p in players if p != player]
        return random.choice(other_players)
    
    def choose_resource(self, game_state, _):
        resources = ["twig", "resin", "pebble", "berry"]
        return random.choice(resources)
    