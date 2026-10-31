from enum import Enum


class StringEnum(str, Enum):
    def __str__(self) -> str:
        return self.value


class ResourceType(StringEnum):
    TWIG = "twig"
    RESIN = "resin"
    PEBBLE = "pebble"
    BERRY = "berry"


class PointCategory(StringEnum):
    CARD = "card"
    TOKEN = "token"
    PROSPERITY = "prosperity"
    JOURNEY = "journey"
    EVENT = "event"


class CityAssetType(StringEnum):
    DESTINATION_WORKERS = "destination_workers"
    STORED_CARDS = "stored_cards"
    CARD_PAIRS = "card_pairs"


class CardStorageKey(StringEnum):
    CARDS = "cards"
    RESOURCES = "resources"
    POINT_TOKENS = "point_tokens"


class Season(StringEnum):
    WINTER = "winter"
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"


class LocationType(StringEnum):
    TEMPORARY = "temporary"
    PERMANENT = "permanent"
    BASIC = "basic"
    FOREST = "forest"
    BASIC_EVENT = "basic_event"
    SPECIAL_EVENT = "special_event"
    DESTINATION_CARD = "destination_card"
    HAVEN = "haven"
    JOURNEY = "journey"


class GameMode(StringEnum):
    SCENARIO = "scenario"
    SIMULATION = "simulation"


class PlayTag(StringEnum):
    EXTERNAL_PLAY_ABILITY = "external_play_ability"


class CardZone(StringEnum):
    HAND = "hand"
    CITY = "city"
    MEADOW = "meadow"
    DECK = "deck"
    DISCARD_PILE = "discardpile"


class DecisionKind(StringEnum):
    MOVE = "move"
    CARD_NEW = "card_new"
    CARD_PLAY_METHOD = "card_play_method"
    CARD_HAND_OR_MEADOW = "card_hand_or_meadow"
    CARD_DECK_OR_DISCARD_PILE = "card_deck_or_discardpile"
    CARD_DISCARD = "card_discard"
    CARD_REACTIVATE_GREEN = "card_reactivate_green"
    CARDS_TO_TAKE_HAND = "cards_to_take_hand"
    CARDS_TO_STORE = "cards_to_store"
    NR_CARDS_DISCARD_HAND = "nr_cards_discard_hand"
    LOCATION_PLACE_WORKER = "location_place_worker"
    LOCATION_ACTIVATE_WITH_POINT_TOKEN = "location_activate_with_point_token"
    LOCATION_TAKE_WORKER = "location_take_worker"
    LOCATION_COPY_ACTION = "location_copy_action"
    LOCATION_REPLACE_WORKER = "location_replace_worker"
    RESOURCE_NEW = "resource_new"
    RESOURCE_DISCARD = "resource_discard"
    RESOURCE_GIVE_AWAY = "resource_give_away"
    NR_RESOURCES_SWAP = "nr_resources_swap"
    NR_RESOURCES_FOR_POINTS = "nr_resources_for_points"
    RESOURCES_TO_LOCATION = "resources_to_location"
    PLAYER_TO_RECEIVE_RESOURCES = "player_to_receive_resources"
    PLAYER_TO_RECEIVE_CARDS_HAND = "player_to_receive_cards_hand"
    PLAYER_TO_RECEIVE_CARDS_CITY = "player_to_receive_cards_city"


class CardType(StringEnum):
    CRITTER = "critter"
    CONSTRUCTION = "construction"


class CardColor(StringEnum):
    PURPLE = "purple"
    TAN = "tan"
    GREEN = "green"
    BLUE = "blue"
    RED = "red"


class PlayMethodKind(StringEnum):
    RECHTER_SUBSTITUTION = "rechter_substitution"
    KRAAN_DISCOUNT = "kraan_discount"
    HERBERGIER_DISCOUNT = "herbergier_discount"
    KERKER_DISCOUNT = "kerker_discount"
    FREE_NO_PAY = "free_no_pay"
    PAY_RESOURCES = "pay_resources"
    RELATED_FREE = "related_free"


class RequirementKind(StringEnum):
    MIN_COLOR_CARDS = "min_color_cards"
    REQUIRED_CARDS_IN_CITY = "required_cards_in_city"
    MIN_CARDS_OF_TYPE = "min_cards_of_type"
    HAS_RESOURCE_TYPE = "has_resource_type"
    HAS_ANY_RESOURCE = "has_any_resource"
    HAS_TOTAL_RESOURCES = "has_total_resources"
    HAS_HAND_CARDS = "has_hand_cards"
    OTHER_PLAYER_HAS_HAND_SPACE = "other_player_has_hand_space"
    HAS_PLACED_WORKER = "has_placed_worker"
    HAS_CITY_CARDS = "has_city_cards"
    HAS_CITY_SPACE = "has_city_space"
    OTHER_PLAYER_HAS_CITY_SPACE = "other_player_has_city_space"
    HAS_PLAYABLE_MEADOW_CARD = "has_playable_meadow_card"
    HAS_PLAYABLE_CARD_WITH_MAX_POINTS = "has_playable_card_with_max_points"


class ResourcePointMode(StringEnum):
    FIXED_CHOOSE_TYPES = "fixed_choose_types"
    MAX_FIXED_TYPE = "max_fixed_type"
    MAX_CHOOSE_TYPES = "max_choose_types"


class GameMove(StringEnum):
    PLAY_CARD = "play_card"
    PLACE_WORKER = "place_worker"
    ADVANCE_SEASON = "advance_season"


class PlayTiming(StringEnum):
    PRE_PLACE = "pre_place"
    POST_PLACE = "post_place"
