from Class_Action import *


class Card:
    def __init__(self, name, color, requirements,
                 cardsindeck, unique, points,
                 action_on_play=None,
                 action_on_reactivate=None,
                 action_on_discard=None):
        self.name = name
        self.color = color
        self.requirements = requirements
        self.cardsindeck = cardsindeck
        self.unique = unique
        self.points = points
        self.action_on_play = action_on_play
        self.action_on_reactivate = action_on_reactivate
        self.action_on_discard = action_on_discard
        
    def __str__(self):
        return str(self.name)

class Critter(Card):
    def __init__(self, name, color, requirements, 
                 cardsindeck, unique, points,
                 action_on_play=None,
                 action_on_reactivate=None,
                 action_on_discard=None):
        super().__init__(name, color, requirements, 
                         cardsindeck, unique, points,
                         action_on_play=action_on_play,
                         action_on_reactivate=action_on_reactivate,
                         action_on_discard=action_on_discard)

class Construction(Card):
    def __init__(self, name, color, requirements, 
                 cardsindeck, unique, points, relatedcritters,
                 action_on_play=None,
                 action_on_reactivate=None,
                 action_on_discard=None):
        super().__init__(name, color, requirements, 
                         cardsindeck, unique, points,
                         action_on_play=action_on_play,
                         action_on_reactivate=action_on_reactivate,
                         action_on_discard=action_on_discard)
        self.relatedcritters = relatedcritters
        self.relatedoccupied = False


cards_unique = []


# ============================================
# CRITTERS (sorted alphabetically)
# ============================================

# To do: Rechter
# To do: For blue critters action on play is not really relevant, how to model?

historicus = Critter(
    name="Historicus",
    color="blue",
    requirements=dict(twig=0, resin=0, pebble=0, berry=2),
    cardsindeck=3,
    unique=True,
    points=1,
    action_on_play=action_draw_cards_from_deck(1),
    action_on_discard=action_remove_card_from_city("Historicus"))

kikkerkapitein = Critter(
    name="Kikkerkapitein",
    color="green",
    requirements=dict(twig=0, resin=0, pebble=0, berry=2),
    cardsindeck=3,
    unique=False,
    points=1,
    action_on_play=action_gain_resource_per_other_card("Boerderij", "twig", 2),
    action_on_discard=action_remove_card_from_city("Kikkerkapitein"))

monnik = Critter(
    name="Monnik",
    color="green",
    requirements=dict(twig=0, resin=0, pebble=0, berry=1),
    cardsindeck=2,
    unique=True,
    points=0,

    action_on_play=CompositeAction([
        action_points_for_given_resources(
            max_nr_resources=2, resource_type="berry", points_per_resource=2),
        action_add_destination_if_card_present(
            "Klooster 2", "destination_card", False, 1,
            action_points_for_given_resources(nr_resources=2, points=4),
            check_card_name="Klooster", permanent_workers=True)]),

    action_on_reactivate=action_points_for_given_resources(
        max_nr_resources=2, resource_type="berry", points_per_resource=2),

    action_on_discard=CompositeAction([
        action_remove_destination("Klooster 2"),
        action_remove_card_from_city("Monnik")]))

winkelier = Critter(
    name="Winkelier",
    color="blue",
    requirements=dict(twig=0, resin=0, pebble=0, berry=2),
    cardsindeck=3,
    unique=True,
    points=1,
    action_on_play=action_gain_resource("berry", 1),
    action_on_discard=action_remove_card_from_city("Winkelier"))


cards_unique.append(historicus)
cards_unique.append(kikkerkapitein)
cards_unique.append(monnik)
cards_unique.append(winkelier)


# ============================================
# CONSTRUCTIONS (sorted alphabetically)
# ============================================

# To do: For blue constructions, action on play is not really relevant
# how to model?

boerderij = Construction(
    name="Boerderij",
    color="green",
    requirements=dict(twig=2, resin=1, pebble=0, berry=0),
    cardsindeck=8,
    unique=False,
    points=1,
    relatedcritters=["Man", "Vrouw"],
    action_on_play=action_gain_resource("berry", 1),
    action_on_reactivate=action_gain_resource("berry", 1),
    action_on_discard=action_remove_card_from_city("Boerderij"))

gerechtsgebouw = Construction(
    name="Gerechtsgebouw",
    color="blue",
    requirements=dict(twig=1, resin=1, pebble=2, berry=0),
    cardsindeck=2,
    unique=True,
    points=2,
    relatedcritters=["Rechter"],
    action_on_play=action_gain_resources_by_choice(
        ["twig", "resin", "pebble"], 1),
    action_on_discard=action_remove_card_from_city("Gerechtsgebouw"))

harsraffinaderij = Construction(
    name="Harsraffinaderij",
    color="green",
    requirements=dict(twig=0, resin=1, pebble=1, berry=0),
    cardsindeck=3,
    unique=False,
    points=1,
    relatedcritters=["Schoonmaker"],
    action_on_play=action_gain_resource("resin", 1),
    action_on_reactivate=action_gain_resource("resin", 1),
    action_on_discard=action_remove_card_from_city("Harsraffinaderij"))

kermis = Construction(
    name="Kermis",
    color="green",
    requirements=dict(twig=1, resin=2, pebble=1, berry=0),
    cardsindeck=3,
    unique=False,
    points=3,
    relatedcritters=["Dwaas"],
    action_on_play=action_draw_cards_from_deck(2),
    action_on_reactivate=action_draw_cards_from_deck(2),
    action_on_discard=action_remove_card_from_city("Kermis"))

klooster = Construction(
    name="Klooster",
    color="red",
    requirements=dict(twig=1, resin=1, pebble=1, berry=0),
    cardsindeck=2,
    unique=True,
    points=1,
    relatedcritters=["Monnik"],
    action_on_play=CompositeAction([
        action_add_destination_card_as_location(
            "Klooster 1", "destination_card", False, 1, 
            action_points_for_given_resources(nr_resources=2, points=4),
            permanent_workers=True),
        action_add_destination_if_card_present(
            "Klooster 2", "destination_card", False, 1,
            action_points_for_given_resources(nr_resources=2, points=4),
            check_card_name="Monnik", permanent_workers=True)]),
    
    action_on_discard=CompositeAction([
            action_remove_destination("Klooster 1"),
            action_remove_destination("Klooster 2"),
            action_remove_card_from_city("Klooster")]))

mijn = Construction(
    name="Mijn",
    color="green",
    requirements=dict(twig=1, resin=1, pebble=1, berry=0),
    cardsindeck=3,
    unique=False,
    points=2,
    relatedcritters=["Mijnwerker mol"],
    action_on_play=action_gain_resource("pebble", 1),
    action_on_reactivate=action_gain_resource("pebble", 1),
    action_on_discard=action_remove_card_from_city("Mijn"))

takkenboot = Construction(
    name="Takkenboot",
    color="green",
    requirements=dict(twig=1, resin=0, pebble=1, berry=0),
    cardsindeck=3,
    unique=False,
    points=1,
    relatedcritters=["Kikkerkapitein"],
    action_on_play=action_gain_resource("twig", 2),
    action_on_reactivate=action_gain_resource("twig", 2),
    action_on_discard=action_remove_card_from_city("Takkenboot"))

universiteit = Construction(
    name="Universiteit",
    color="red",
    requirements=dict(twig=0, resin=1, pebble=2, berry=0),
    cardsindeck=2,
    unique=True,
    points=3,
    relatedcritters=["Dokter"],
    action_on_play=action_add_destination_card_as_location(
        "Universiteit", "destination_card", False, 1, CompositeAction([
            action_gain_resources_building_costs_discard(True, True),
            action_gain_resources_by_choice(
                ["twig", "resin", "pebble", "berry"], 1),
            action_gain_points("token", 1)])),

    action_on_discard=CompositeAction([
        action_remove_destination("Universiteit"),
        action_remove_card_from_city("Universiteit")]))

winkel = Construction(
    name="Winkel",
    color="green",
    requirements=dict(twig=0, resin=1, pebble=1, berry=0),
    cardsindeck=3,
    unique=False,
    points=1,
    relatedcritters=["Winkelier"],
    action_on_play=CompositeAction([action_gain_resource("berry", 1), 
    action_gain_resource_if_other_card("Boerderij", "berry", 1)]),
    action_on_reactivate=CompositeAction([action_gain_resource("berry", 1), 
    action_gain_resource_if_other_card("Boerderij", "berry", 1)]),
    action_on_discard=action_remove_card_from_city("Winkel"))


cards_unique.append(boerderij)
cards_unique.append(gerechtsgebouw)
cards_unique.append(harsraffinaderij)
cards_unique.append(kermis)
cards_unique.append(klooster)
cards_unique.append(mijn)
cards_unique.append(takkenboot)
cards_unique.append(universiteit)
cards_unique.append(winkel)


# ============================================
# INITIATE CARDS WITH THE RIGHT QUANTITY
# ============================================

init_cards = []
for c in cards_unique:
    init_cards.extend([c] * c.cardsindeck)
