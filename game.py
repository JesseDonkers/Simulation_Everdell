from class_deck import Deck
from class_discard_pile import DiscardPile
from class_meadow import Meadow
from class_player import Player
from class_action import *
from class_card import init_cards
from class_location import init_locations
from class_strategy import *
from functions_statistics import *
from functions_testing import *

import copy


# ============================================
# VARIABLES & PARAMETERS
# ============================================

NR_SIMULATION_RUNS = 100
NR_PLAYERS = 2 # Number of players in the game (2-4)
STRATEGY_PER_PLAYER = [Strategy_random, Strategy_random]


# ============================================
# INITIATE SIMULATION RUNS AND RESULTS
# ============================================

clear_test_results()

for _ in range(NR_SIMULATION_RUNS):


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

    players = [Player() for _ in range(NR_PLAYERS)]
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
    if len(STRATEGY_PER_PLAYER) != len(players):
        raise ValueError(f"Number of strategies ({len(STRATEGY_PER_PLAYER)})"   
                        f"does not match number of players ({len(players)})")
    for p in range(len(players)):
        players[p].strategy = STRATEGY_PER_PLAYER[p]()


    # ============================================
    # EXECUTING GAME
    # ============================================

    player: "Player" = game_state["current_player"]

    player.resources_add("twig", 5)
    player.resources_add("resin", 5)
    player.resources_add("pebble", 5)

    action_play_card().execute(game_state)

    game_state_as_df_to_text(game_state, "Game_state")

    player.city[0].action_on_discard.execute(game_state)

    game_state_as_df_to_text(game_state, "Game_state")

    break

    
    # ============================================
    # END GAME
    # ============================================

    # No more possible actions or every player has passed
    # Winner is the one with the most points, when tie, most resources

