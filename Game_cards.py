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


# ============================================
# CONSTRUCTIONS
# ============================================

boerderij = Construction()
boerderij.name = "Boerderij"
boerderij.color = "green"
boerderij.requirements = dict(twig=2, resin=1, pebble=0, berry=0)
boerderij.unique = False
boerderij.points = 1
boerderij.relatedcritter = ["Man", "Vrouw"]
boerderij.action = action_gain_resource('berry', 1)
cards.extend([boerderij] * 99)

