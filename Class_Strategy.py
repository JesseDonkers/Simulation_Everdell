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

    def choose_card_hand_or_meadow(self, game_state, _):
        opt = ["hand", "meadow"]
        return random.choice(opt)
    
    def choose_card_deck_or_discardpile(self, game_state, _):
        opt = ["deck", "discardpile"]
        return random.choice(opt)
    
    def choose_nr_cards_discard_hand(self, game_state, _):
        player = game_state["current_player"]
        max_nr = len(player.hand)
        return random.randint(0, max_nr)
    
    def choose_card_discard(self, game_state, possible_cards):
        return random.choice(possible_cards)

    def choose_location(self, game_state, possible_locations):
        return random.choice(possible_locations)
    
    def choose_resource_new(self, game_state, _):
        resources = ["twig", "resin", "pebble", "berry"]
        return random.choice(resources)
    
    def choose_resource_give_away(self, game_state, quantity):
        player = game_state["current_player"]
        available = {r: player.resources.get(r, 0) for r in 
                     ("twig", "resin", "pebble", "berry")}
        picks = []

        for _ in range(quantity):
            options = [r for r, cnt in available.items() if cnt > 0]
            choice = random.choice(options)
            picks.append(choice)
            available[choice] -= 1
        return picks

    def choose_nr_resources_to_give_away(self, game_state, nr_and_type):
        player = game_state["current_player"]
        max_nr_resources = nr_and_type[0]
        resource_type = nr_and_type[1]
        available_resources = player.resources.get(resource_type)
        return random.randint(0, min(max_nr_resources, available_resources))
    
    def choose_nr_resources_to_pay(self, game_state, nr_and_type):
        player = game_state["current_player"]
        max_nr_resources = nr_and_type[0]
        resource_type = nr_and_type[1]
        available_resources = player.resources.get(resource_type)
        return random.randint(0, min(max_nr_resources, available_resources))
    
    def choose_player_to_receive_resources(self, game_state, _):
        player = game_state["current_player"]
        players = game_state["players"]
        other_pls = [p for p in players if p != player and p.finished == False]
        return random.choice(other_pls)
    
    def choose_player_to_receive_cards(self, game_state, nr_give):
        player = game_state["current_player"]
        players = game_state["players"]
        other_pls = [p for p in players
                     if p != player
                     and not p.finished
                     and p.cards_get_open_spaces("hand") >= nr_give]
        return random.choice(other_pls)
