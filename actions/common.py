def action_is_in_tree(action_root, target_action):
    if action_root is target_action:
        return True

    child_actions = getattr(action_root, "actions", None)
    if child_actions is None:
        return False

    return any(
        action_is_in_tree(sub_action, target_action) for sub_action in child_actions
    )


def resolve_city_card_target(
    player, action_obj, card=None, card_id=None, card_name=None
):
    if card is not None:
        if card not in player.city:
            raise ValueError("Target card is not in player's city")
        return card

    if card_id is not None:
        target_card = next(
            (
                city_card
                for city_card in player.city
                if getattr(city_card, "card_id", None) == card_id
            ),
            None,
        )
        if target_card is None:
            raise ValueError(f"No city card found with card_id {card_id}")
        return target_card

    for city_card in player.city:
        for action_attr in (
            "action_on_play",
            "action_on_reactivate",
            "action_on_discard",
        ):
            city_card_action = getattr(city_card, action_attr, None)
            if city_card_action and action_is_in_tree(city_card_action, action_obj):
                return city_card

    if card_name is not None:
        matching_cards = [
            city_card for city_card in player.city if city_card.name == card_name
        ]
        if len(matching_cards) == 1:
            return matching_cards[0]
        if len(matching_cards) > 1:
            raise ValueError(
                f"Ambiguous card target for name '{card_name}'. Provide card or card_id."
            )

    raise ValueError("Could not resolve target city card")
