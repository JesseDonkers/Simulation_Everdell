import random


# ============================================
# BASE STRATEGY CLASS
# ============================================

class Strategy():
    def decide(self, game_state, decision_kind, parameters):
        handler_name = f"choose_{decision_kind}"
        handler = getattr(self, handler_name, None)

        if handler is None:
            raise ValueError(f"Unknown decision type: {decision_kind}")
        return handler(game_state, parameters)


# ============================================
# CLASS PER STRATEGY
# ============================================

class Strategy_random(Strategy):
    def choose_move(self, game_state, possible_moves):
        return random.choice(possible_moves)

    def choose_card_new(self, game_state, possible_cards):
        return random.choice(possible_cards)

    def choose_card_play_method(self, game_state, possible_methods):
        return random.choice(possible_methods)

    def choose_card_hand_or_meadow(self, game_state, _):
        opt = ["hand", "meadow"]
        return random.choice(opt)
    
    def choose_card_deck_or_discardpile(self, game_state, _):
        opt = ["deck", "discardpile"]
        return random.choice(opt)
    
    def choose_nr_cards_discard_hand(self, game_state, max_nr):
        return random.randint(0, max_nr)
    
    def choose_card_discard(self, game_state, possible_cards):
        return random.choice(possible_cards)
    
    def choose_card_reactivate_green(self, game_state, possible_cards):
        return random.choice(possible_cards)    

    def choose_location_place_worker(self, game_state, possible_locations):
        return random.choice(possible_locations)

    def choose_location_take_worker(self, game_state, possible_locations):
        return random.choice(possible_locations)
    
    def choose_resource_new(self, game_state, _):
        resources = ["twig", "resin", "pebble", "berry"]
        return random.choice(resources)
    
    def choose_resource_give_away(self, game_state, parameters):
        nr_to_pick, available = parameters
        pool = [r for r, count in available.items() for _ in range(count)]
        return random.sample(pool, nr_to_pick)

    def choose_nr_resources_to_give_away(self, game_state, max_nr_resources):
        return random.randint(0, max_nr_resources)
    
    def choose_nr_resources_for_points(self, game_state, max_nr_resources):
        return random.randint(0, max_nr_resources)
    
    def choose_player_to_receive_resources(self, game_state, possible_players):
        return random.choice(possible_players)
    
    def choose_player_to_receive_cards(self, game_state, possible_players):
        return random.choice(possible_players)
