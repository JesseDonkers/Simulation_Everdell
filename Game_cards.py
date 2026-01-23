from Class_Card import Critter, Construction
from Class_Action import *


cards = []

# ============================================
# CRITTERS
# ============================================

historicus = Critter("Historicus","blue", dict(twig=0, resin=0, pebble=0, berry=2), 
                        3, True, 1, action_draw_cards_from_deck(1), "Klokkentoren")
winkelier = Critter("Winkelier", "blue", dict(twig=0, resin=0, pebble=0, berry=2),
                        3, True, 1, action_gain_resource("berry", 1), "Winkel")
# To do: Rechter

kikkerkapitein = Critter("Kikkerkapitein", "green", 
                         dict(twig=0, resin=0, pebble=0, berry=2), 3, False, 1, 
                         action_gain_resource_per_other_card("Boerderij", "twig", 2), 
                         "Takkenboot")



cards.extend([historicus] * 30) # To do: should be xx.cardsindeck
cards.extend([winkelier] * 30) # To do: should be xx.cardsindeck
cards.extend([kikkerkapitein] * 30) # To do: should be xx.cardsindeck


# ============================================
# CONSTRUCTIONS
# ============================================

boerderij = Construction("Boerderij", "green", dict(twig=2, resin=1, pebble=0, berry=0), 
                        8, False, 1, action_gain_resource("berry", 1), ["Man", "Vrouw"])
takkenboot = Construction("Takkenboot", "green", dict(twig=1, resin=0, pebble=1, berry=0),
                        3, False, 1, action_gain_resource("twig", 2), ["Kikkerkapitein"])
winkel = Construction("Winkel", "green", dict(twig=0, resin=1, pebble=1, berry=0),
                        3, False, 1, CompositeAction([action_gain_resource("berry", 1), 
                        action_gain_resource_if_other_card("Boerderij", "berry", 1)]), 
                        ["Kikkerkapitein"])
mijn = Construction("Mijn", "green", dict(twig=1, resin=1, pebble=1, berry=0),
                        3, False, 2, action_gain_resource("pebble", 1), ["Mijnwerker mol"])
harsraffinaderij = Construction("Harsraffinaderij", "green", dict(twig=0, resin=1, pebble=1, berry=0),
                        3, False, 1, action_gain_resource("resin", 1), ["Schoonmaker"])
kermis = Construction("Kermis", "green", dict(twig=1, resin=2, pebble=1, berry=0),
                        3, False, 3, action_draw_cards_from_deck(2), ["Dwaas"])

cards.extend([boerderij] * 30) # To do: should be xx.cardsindeck
cards.extend([takkenboot] * 30) # To do: should be xx.cardsindeck
cards.extend([winkel] * 30) # To do: should be xx.cardsindeck
cards.extend([mijn] * 30) # To do: should be xx.cardsindeck
cards.extend([harsraffinaderij] * 30) # To do: should be xx.cardsindeck
cards.extend([kermis] * 30) # To do: should be xx.cardsindeck
