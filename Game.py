from Class_Deck import Deck
from Class_DiscardPile import DiscardPile
from Class_Meadow import Meadow
from Class_Player import Player
from Class_Card import init_cards
from Class_Location import init_locations
from Class_Strategy import *
from Functions_game import *
from Functions_statistics import *

import copy


# ============================================
# VARIABLES & PARAMETERS
# ============================================

nr_simulation_runs = 1
nrPlayers = 2 # Number of players in the game (2-4)
strategy_per_player = [Strategy_random, Strategy_random]


# ============================================
# INITIATE SIMULATION RUNS AND RESULTS
# ============================================

for _ in range(nr_simulation_runs):


    # ============================================
    # SET UP GAME
    # ============================================

    cards = copy.deepcopy(init_cards)
    deck = Deck()
    deck.add_to_deck(cards)
    deck.shuffle_deck()
    discardpile = DiscardPile()
    meadow = Meadow()
    meadow.add_to_meadow(8, deck, discardpile)

    players = [Player() for _ in range(nrPlayers)]
    card_counter = 5
    for p in players:
        p.index = players.index(p)
        drawn_cards = deck.draw_cards(card_counter, discardpile)
        p.cards_add(drawn_cards, "hand")
        card_counter += 1 # Each successive player draws one more card
        p.workers_add(2) # Each player starts with 2 workers


    # To do:
    #  - Shuffle special events
    #  - Draw 4 special events (add to locations)
    #  - Shuffle forest cards
    #  - Place 3 or 4 forecst cards depending on nr players (add to locations)


    game_state = {
        "deck": deck,
        "discardpile": discardpile,
        "meadow": meadow,
        "locations": copy.deepcopy(init_locations),
        "players": players,
        "current_player": players[0],
    }


    # Each player is provided with a strategy.
    if len(strategy_per_player) != len(players):
        raise ValueError(f"Number of strategies ({len(strategy_per_player)}) "
                        f"does not match number of players ({len(players)})")
    for p in range(len(players)):
        players[p].strategy = strategy_per_player[p]()


    # ============================================
    # EXECUTING GAME
    # ============================================



    # ============================================
    # END GAME
    # ============================================

    # No more possible actions or every player has passed
    # Winner is the one with the most points, when tie, most resources
