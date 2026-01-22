from Class_Card import Critter, Construction
from Class_Action import *

# cards = ["Peter", "Jan", "Piet", "Klaas", "Peter", "Jan", "Piet", "Klaas", "Cynthia", "Olivia", "Evelyn", "Cynthia", "Olivia",
#          "Evelyn", "George", "Harold", "Irene", "George", "Harold", "Irene", "Farm", "Lodge", "Market", "Farm", "Lodge",
#          "Market", "School", "Store", "Tavern", "School", "Store", "Tavern", "Workshop", "Bridge", "Cathedral",
#          "Peter", "Jan", "Piet", "Klaas", "Peter", "Jan", "Piet", "Klaas", "Cynthia", "Olivia", "Evelyn", "Cynthia", "Olivia",
#          "Evelyn", "George", "Harold", "Irene", "George", "Harold", "Irene", "Farm", "Lodge", "Market", "Farm", "Lodge",
#          "Market", "School", "Store", "Tavern", "School", "Store", "Tavern", "Workshop", "Bridge", "Cathedral"]

cards = []

# ============================================
# CRITTERS
# ============================================

historicus = Critter("Historicus","Blue", dict(twig=0, resin=0, pebble=0, berry=2), 
                     3, True, 1, action_draw_cards_from_deck(1), "Klokkentoren")

cards.extend([historicus] * 99) # To do: should be historicus.cardsindeck


# ============================================
# CONSTRUCTIONS
# ============================================

boerderij = Construction(
    "Boerderij", "green", dict(twig=2, resin=1, pebble=0, berry=0),
    8, False, 1, action_gain_resource('berry', 1), ["Man", "Vrouw"])

cards.extend([boerderij] * 99) # To do: 99 should be boerderij.cardsindeck

