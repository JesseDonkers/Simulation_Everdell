import copy

from actions import cards
from class_action import *


class Card:
    def __init__(self, name, color, costs,
                 cardsindeck, unique, points,
                 action_on_play=None,
                 action_on_reactivate=None,
                 action_on_discard=None,
                 action_on_finish=None,
                 requirements=None):
        self.name = name
        self.color = color
        self.costs = costs
        self.cardsindeck = cardsindeck
        self.unique = unique
        self.points = points
        self.action_on_play = action_on_play
        self.action_on_reactivate = action_on_reactivate
        self.action_on_discard = action_on_discard
        self.action_on_finish = action_on_finish
        self.requirements = requirements  # Optional play preconditions
        self.stored_cards = []  # For cards attached to this card (e.g. Kerker)
        
    def __str__(self):
        return str(self.name)

class Critter(Card):
    def __init__(self, name, color, costs,
                 cardsindeck, unique, points,
                 action_on_play=None,
                 action_on_reactivate=None,
                 action_on_discard=None,
                 action_on_finish=None,
                 requirements=None):
        super().__init__(name, color, costs,
                         cardsindeck, unique, points,
                         action_on_play=action_on_play,
                         action_on_reactivate=action_on_reactivate,
                         action_on_discard=action_on_discard,
                         action_on_finish=action_on_finish,
                         requirements=requirements)

class Construction(Card):
    def __init__(self, name, color, costs,
                 cardsindeck, unique, points, relatedcritters,
                 action_on_play=None,
                 action_on_reactivate=None,
                 action_on_discard=None,
                 action_on_finish=None,
                 requirements=None):
        super().__init__(name, color, costs,
                         cardsindeck, unique, points,
                         action_on_play=action_on_play,
                         action_on_reactivate=action_on_reactivate,
                         action_on_discard=action_on_discard,
                         action_on_finish=action_on_finish,
                         requirements=requirements)
        self.relatedcritters = relatedcritters
        self.relatedoccupied = False


cards_unique = []


# ============================================
# CRITTERS (sorted alphabetically)
# ============================================

architect = Critter(
    name="Architect",
    color="purple",
    costs=dict(twig=0, resin=0, pebble=0, berry=4),
    cardsindeck=2,
    unique=True,
    points=2,
    action_on_finish=actions_points_for_resources_hand(["resin", "pebble"], 1),
    action_on_discard=action_remove_card_from_city("Architect"))

begrafenisondernemer = Critter(
    name="Begrafenisondernemer",
    color="tan",
    costs=dict(twig=0, resin=0, pebble=0, berry=2),
    cardsindeck=2,
    unique=True,
    points=1,

    action_on_play=CompositeAction([
        action_refresh_meadow_draw_cards(3),
        action_add_destination_if_card_present(
            "Begraafplaats 2", "destination_card", 1,
            action_play_cards_from_deck_or_discardpile(4), 
            check_card_name="Begraafplaats", permanent_workers=True)]),

    action_on_discard=CompositeAction([
        action_remove_destination("Begraafplaats 2"),
        action_remove_card_from_city("Begrafenisondernemer")]))

boswachter = Critter(
    name="Boswachter",
    color="tan",
    costs=dict(twig=0, resin=0, pebble=0, berry=2),
    cardsindeck=2,
    unique=True,
    points=1,
    action_on_play=action_replace_worker(),
    action_on_discard=action_remove_card_from_city("Boswachter"),
    requirements={"kind": "has_placed_worker"})

dokter = Critter(
    name="Dokter",
    color="green",
    costs=dict(twig=0, resin=0, pebble=0, berry=4),
    cardsindeck=2,
    unique=True,
    points=4,
    action_on_play=action_points_for_payed_resources(3, "berry", 1),
    action_on_reactivate=action_points_for_payed_resources(3, "berry", 1),
    action_on_discard=action_remove_card_from_city("Dokter"))

# To do: dwaas

# To do: herbergier

# To do: herder

historicus = Critter(
    name="Historicus",
    color="blue",
    costs=dict(twig=0, resin=0, pebble=0, berry=2),
    cardsindeck=3,
    unique=True,
    points=1,
    action_on_play=action_cards_from_deck_to_hand(1),
    action_on_discard=action_remove_card_from_city("Historicus"))

houtsnijder = Critter(
    name="Houtsnijder",
    color="green",
    costs=dict(twig=0, resin=0, pebble=0, berry=2),
    cardsindeck=3,
    unique=False,
    points=2,
    action_on_play=action_points_for_payed_resources(3, "twig", 1),
    action_on_reactivate=action_points_for_payed_resources(3, "twig", 1),
    action_on_discard=action_remove_card_from_city("Houtsnijder"))

kikkerkapitein = Critter(
    name="Kikkerkapitein",
    color="green",
    costs=dict(twig=0, resin=0, pebble=0, berry=2),
    cardsindeck=3,
    unique=False,
    points=1,
    action_on_play=action_resource_per_other_card(
                                                    "Boerderij", "twig", 2),
    action_on_reactivate=action_resource_per_other_card(
                                                    "Boerderij", "twig", 2),
    action_on_discard=action_remove_card_from_city("Kikkerkapitein"))

# To do: leraar

# To do: koning

koningin = Critter(
    name="Koningin",
    color="red",
    costs=dict(twig=0, resin=0, pebble=0, berry=5),
    cardsindeck=2,
    unique=True,
    points=4,
    action_on_play=action_add_destination_card_as_location(
        "Koningin",
        "destination_card",
        1,
        action_play_card(3, False),
        requirements={
            "kind": "has_playable_card_with_max_points",
            "max_points": 3,
        },
    ),
    action_on_discard=CompositeAction(
        [action_remove_destination("Koningin"),
         action_remove_card_from_city("Koningin")]))

# To do: man

# To do: marskramer

# To do: mijnwerkermol

monnik = Critter(
    name="Monnik",
    color="green",
    costs=dict(twig=0, resin=0, pebble=0, berry=1),
    cardsindeck=2,
    unique=True,
    points=0,

    action_on_play=CompositeAction([
        action_points_for_given_resources(
            max_nr_resources=2, resource_type="berry", points_per_resource=2),
        action_add_destination_if_card_present(
            "Klooster 2", "destination_card", 1,
            action_points_for_given_resources(nr_resources=2, points=4),
            check_card_name="Klooster",
            permanent_workers=True,
            requirements={"kind": "has_resource_type",
                          "resource": "berry", "amount": 1})]),

    action_on_reactivate=action_points_for_given_resources(
        max_nr_resources=2, resource_type="berry", points_per_resource=2),

    action_on_discard=CompositeAction(
        [action_remove_destination("Klooster 2"),
         action_remove_card_from_city("Monnik")]))

# To do: postduif

# To do: rechter

# To do: schoonmaker

# To do: vrouw

winkelier = Critter(
    name="Winkelier",
    color="blue",
    costs=dict(twig=0, resin=0, pebble=0, berry=2),
    cardsindeck=3,
    unique=True,
    points=1,
    # To do: when a critter is played
    action_on_play=action_resource_general("berry", 1),
    action_on_discard=action_remove_card_from_city("Winkelier"))

zanger = Critter(
    name="Zanger",
    color="tan",
    costs=dict(twig=0, resin=0, pebble=0, berry=3),
    cardsindeck=2,
    unique=True,
    points=0,
    action_on_play=action_points_for_discarding_cards(5, 1),
    action_on_discard=action_remove_card_from_city("Zanger"))

# To do: zwerver


cards_unique.append(architect)
cards_unique.append(begrafenisondernemer)
cards_unique.append(boswachter)
cards_unique.append(dokter)
cards_unique.append(historicus)
cards_unique.append(houtsnijder)
cards_unique.append(kikkerkapitein)
cards_unique.append(koningin)
cards_unique.append(monnik)
cards_unique.append(winkelier)
cards_unique.append(zanger)


# ============================================
# CONSTRUCTIONS (sorted alphabetically)
# ============================================

begraafplaats = Construction(
    name="Begraafplaats",
    color="red",
    costs=dict(twig=0, resin=0, pebble=2, berry=0),
    cardsindeck=2,
    unique=True,
    points=0,
    relatedcritters=["Begrafenisondernemer"],

    action_on_play=CompositeAction([
        action_add_destination_card_as_location(
            "Begraafplaats 1",
            "destination_card",
            1,
            action_play_cards_from_deck_or_discardpile(4),
            permanent_workers=True,
            requirements={"kind": "has_city_space"},
        ),
        action_add_destination_if_card_present(
            "Begraafplaats 2",
            "destination_card",
            1,
            action_play_cards_from_deck_or_discardpile(4),
            check_card_name="Begrafenisondernemer",
            permanent_workers=True,
            requirements={"kind": "has_city_space"},
        )]),

    action_on_discard=CompositeAction([
            action_remove_destination("Begraafplaats 1"),
            action_remove_destination("Begraafplaats 2"),
            action_remove_card_from_city("Begraafplaats")]))

    # To do: add requirement for placing worker: space in city

boerderij = Construction(
    name="Boerderij",
    color="green",
    costs=dict(twig=2, resin=1, pebble=0, berry=0),
    cardsindeck=8,
    unique=False,
    points=1,
    relatedcritters=["Man", "Vrouw"],
    action_on_play=action_resource_general("berry", 1),
    action_on_reactivate=action_resource_general("berry", 1),
    action_on_discard=action_remove_card_from_city("Boerderij"))

# To do: evertree

gerechtsgebouw = Construction(
    name="Gerechtsgebouw",
    color="blue",
    costs=dict(twig=1, resin=1, pebble=2, berry=0),
    cardsindeck=2,
    unique=True,
    points=2,
    relatedcritters=["Rechter"],
    action_on_play=action_resources_by_choice(
        ["twig", "resin", "pebble"], 1),
    action_on_discard=action_remove_card_from_city("Gerechtsgebouw"))

harsraffinaderij = Construction(
    name="Harsraffinaderij",
    color="green",
    costs=dict(twig=0, resin=1, pebble=1, berry=0),
    cardsindeck=3,
    unique=False,
    points=1,
    relatedcritters=["Schoonmaker"],
    action_on_play=action_resource_general("resin", 1),
    action_on_reactivate=action_resource_general("resin", 1),
    action_on_discard=action_remove_card_from_city("Harsraffinaderij"))

herberg = Construction(
    name="Herberg",
    color="red",
    costs=dict(twig=2, resin=1, pebble=0, berry=0),
    cardsindeck=3,
    unique=False,
    points=2,
    relatedcritters=["Herbergier"],
    action_on_play=action_add_destination_card_as_location(
        "Herberg", "destination_card", 1,
        action_play_meadow_card_with_discount(3),
        is_open=True,
        requirements={"kind": "has_playable_meadow_card", "discount": 3}),
    action_on_discard=CompositeAction([
        action_remove_destination("Herberg"),
        action_remove_card_from_city("Herberg")]))

# To do: kapel

kasteel = Construction(
    name="Kasteel",
    color="purple",
    costs=dict(twig=2, resin=3, pebble=3, berry=0),
    cardsindeck=2,
    unique=True,
    points=4,
    relatedcritters=["Koning"],    
    action_on_finish=actions_points_for_cards_in_city(
                                                    "Construction", False, 1),
    action_on_discard=action_remove_card_from_city("Kasteel"))

kerker = Construction(
    name="Kerker",
    color="blue",
    costs=dict(twig=0, resin=1, pebble=2, berry=0),
    cardsindeck=2,
    unique=True,
    points=0,
    relatedcritters=["Boswachter"],
    action_on_discard=CompositeAction([
        action_discard_stored_cards("Kerker"),
        action_remove_card_from_city("Kerker")
    ]))

kermis = Construction(
    name="Kermis",
    color="green",
    costs=dict(twig=1, resin=2, pebble=1, berry=0),
    cardsindeck=3,
    unique=False,
    points=3,
    relatedcritters=["Dwaas"],
    action_on_play=action_cards_from_deck_to_hand(2),
    action_on_reactivate=action_cards_from_deck_to_hand(2),
    action_on_discard=action_remove_card_from_city("Kermis"))

# To do: klokkentoren

klooster = Construction(
    name="Klooster",
    color="red",
    costs=dict(twig=1, resin=1, pebble=1, berry=0),
    cardsindeck=2,
    unique=True,
    points=1,
    relatedcritters=["Monnik"],
    action_on_play=CompositeAction([
        action_add_destination_card_as_location(
            "Klooster 1", "destination_card", 1, 
            action_points_for_given_resources(nr_resources=2, points=4),
            permanent_workers=True,
            requirements={"kind": "has_any_resource"}),
        action_add_destination_if_card_present(
            "Klooster 2", "destination_card", 1,
            action_points_for_given_resources(nr_resources=2, points=4),
            check_card_name="Monnik",
            permanent_workers=True,
            requirements={"kind": "has_any_resource"})]),

    action_on_discard=CompositeAction([
        action_remove_destination("Klooster 1"),
        action_remove_destination("Klooster 2"),
        action_remove_card_from_city("Klooster")]))

# To do: kraan

mijn = Construction(
    name="Mijn",
    color="green",
    costs=dict(twig=1, resin=1, pebble=1, berry=0),
    cardsindeck=3,
    unique=False,
    points=2,
    relatedcritters=["Mijnwerker mol"],
    action_on_play=action_resource_general("pebble", 1),
    action_on_reactivate=action_resource_general("pebble", 1),
    action_on_discard=action_remove_card_from_city("Mijn"))

# To do: pakhuis

paleis = Construction(
    name="Paleis",
    color="purple",
    costs=dict(twig=2, resin=3, pebble=3, berry=0),
    cardsindeck=2,
    unique=True,
    points=4,
    relatedcritters=["Koningin"],    
    action_on_finish=actions_points_for_cards_in_city("Construction", True, 1),
    action_on_discard=action_remove_card_from_city("Paleis"))

postkantoor = Construction(
    name="Postkantoor",
    color="red",
    costs=dict(twig=1, resin=2, pebble=0, berry=0),
    cardsindeck=3,
    unique=False,
    points=2,
    relatedcritters=["Postduif"],
    action_on_play=action_add_destination_card_as_location(
        "Postkantoor", "destination_card", 1,
        action_give_discard_refill_hand(2),
        is_open=True,
        requirements=[
            {"kind": "has_hand_cards", "amount": 2},
            {"kind": "other_player_has_hand_space", "amount": 2},
        ]),
    action_on_discard=CompositeAction([
        action_remove_destination("Postkantoor"),
        action_remove_card_from_city("Postkantoor")]))

# To do: ruines

school = Construction(
    name="School",
    color="purple",
    costs=dict(twig=2, resin=2, pebble=0, berry=0),
    cardsindeck=2,
    unique=True,
    points=2,
    relatedcritters=["Leraar"],
    action_on_finish=actions_points_for_cards_in_city("Critter", False, 1),
    action_on_discard=action_remove_card_from_city("School"))

takkenboot = Construction(
    name="Takkenboot",
    color="green",
    costs=dict(twig=1, resin=0, pebble=1, berry=0),
    cardsindeck=3,
    unique=False,
    points=1,
    relatedcritters=["Kikkerkapitein"],
    action_on_play=action_resource_general("twig", 2),
    action_on_reactivate=action_resource_general("twig", 2),
    action_on_discard=action_remove_card_from_city("Takkenboot"))

theater = Construction(
    name="Theater",
    color="purple",
    costs=dict(twig=3, resin=1, pebble=1, berry=0),
    cardsindeck=2,
    unique=True,
    points=3,
    relatedcritters=["Zanger"],
    action_on_finish=actions_points_for_cards_in_city("Critter", True, 1),
    action_on_discard=action_remove_card_from_city("Theater"))

uitkijkpost = Construction(
    name="Uitkijkpost",
    color="red",
    costs=dict(twig=1, resin=1, pebble=1, berry=0),
    cardsindeck=2,
    unique=True,
    points=2,
    relatedcritters=["Zwerver"],
    action_on_play=action_add_destination_card_as_location(
        "Uitkijkpost", "destination_card", 1, 
        action_location_copy_action(["basic", "forest"])),

        # To do: check if requirement is necessary?
        # Copying basic locations is no problem, but forest locations?

    action_on_discard=CompositeAction([
        action_remove_destination("Uitkijkpost"),
        action_remove_card_from_city("Uitkijkpost")]))

universiteit = Construction(
    name="Universiteit",
    color="red",
    costs=dict(twig=0, resin=1, pebble=2, berry=0),
    cardsindeck=2,
    unique=True,
    points=3,
    relatedcritters=["Dokter"],
    action_on_play=action_add_destination_card_as_location(
        "Universiteit",
        "destination_card",
        1,
        CompositeAction([
            action_resources_building_costs_discard(True, True),
            action_resources_by_choice(
                ["twig", "resin", "pebble", "berry"], 1),
            action_points_general("token", 1)]),
        requirements={"kind": "has_city_cards", "amount": 1},
    ),
    action_on_discard=CompositeAction([
        action_remove_destination("Universiteit"),
        action_remove_card_from_city("Universiteit")]))

winkel = Construction(
    name="Winkel",
    color="green",
    costs=dict(twig=0, resin=1, pebble=1, berry=0),
    cardsindeck=3,
    unique=False,
    points=1,
    relatedcritters=["Winkelier"],
    action_on_play=CompositeAction([action_resource_general("berry", 1), 
    action_resource_if_other_card("Boerderij", "berry", 1)]),
    action_on_reactivate=CompositeAction([action_resource_general("berry", 1), 
    action_resource_if_other_card("Boerderij", "berry", 1)]),
    action_on_discard=action_remove_card_from_city("Winkel"))


cards_unique.append(begraafplaats)
cards_unique.append(boerderij)
cards_unique.append(gerechtsgebouw)
cards_unique.append(harsraffinaderij)
cards_unique.append(herberg)
cards_unique.append(kasteel)
cards_unique.append(kerker)
cards_unique.append(kermis)
cards_unique.append(klooster)
cards_unique.append(mijn)
cards_unique.append(paleis)
cards_unique.append(postkantoor)
cards_unique.append(school)
cards_unique.append(takkenboot)
cards_unique.append(theater)
cards_unique.append(universiteit)
cards_unique.append(uitkijkpost)
cards_unique.append(winkel)


# ============================================
# INITIATE CARDS WITH THE RIGHT QUANTITY
# ============================================

init_cards = []
for c in cards_unique:
    for _ in range(c.cardsindeck):
        init_cards.append(copy.deepcopy(c))
