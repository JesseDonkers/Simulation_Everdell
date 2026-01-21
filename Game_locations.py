from Class_Location import Location
from Class_Action import *


locations = []

# ============================================
# BASIC
# ============================================
twigs = Location("Basic", False, 1, [action_gain_resource('twig', 3)])
resins = Location("Basic", False, 1, [action_gain_resource('resin', 2)])
pebble = Location("Basic", False, 1, [action_gain_resource('pebble', 1)])
berry = Location("Basic", False, 99, [action_gain_resource('berry', 1)])

twigsandpoint = Location("Basic", False, 99, CompositeAction(
                                            [action_gain_resource('twig', 2), 
                                            action_gain_points('tokens', 1)]))
resinsandpoint = Location("Basic", False, 99, CompositeAction(
                                            [action_gain_resource('resin', 1), 
                                            action_gain_points('tokens', 1)]))
cardsandpoint = Location("Basic", False, 99, CompositeAction(
                                            [action_gain_points('tokens', 1),
                                            action_draw_cards_from_deck(2)]))
berryandcard = Location("Basic", False, 1, CompositeAction(
                                            [action_gain_resource('berry', 1),
                                            action_draw_cards_from_deck(1)]))

locations.extend([twigs, resins, pebble, berry])
locations.extend([twigsandpoint, resinsandpoint, cardsandpoint, berryandcard])


# ============================================
# FOREST LOCATIONS
# ============================================

# Add constraint for number of workers per player = max 1


# ============================================
# EVENT
# ============================================

# Player will get its worker back, but event stays in the city of the player


# ============================================
# HAVEN
# ============================================


# ============================================
# JOURNEY
# ============================================

# Only accessible in the last season (autumn)