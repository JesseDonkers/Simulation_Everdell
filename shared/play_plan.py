from dataclasses import dataclass
from typing import Any

# Abilities that modify card-play terms (discount, substitution, alternative play)
# share this tag and can conflict with each other.
EXTERNAL_PLAY_ABILITY = "external_play_ability"


@dataclass(frozen=True)
class PlayPlan:
    card: Any
    selected_method: Any
    pre_place_actions: tuple[Any, ...]
    post_place_actions: tuple[Any, ...]


def _get_play_actions(action_root):
    if action_root is None:
        return []

    child_actions = getattr(action_root, "actions", None)
    if child_actions is None:
        return [action_root]

    return list(child_actions)


def build_play_plan(card, selected_method):
    actions = _get_play_actions(getattr(card, "action_on_play", None))
    method_tags = set(getattr(selected_method, "play_tags", ()))
    method_conflicts = set(getattr(selected_method, "play_conflicts", ()))

    pre_place_actions = []
    post_place_actions = []

    for action in actions:
        action_tags = set(getattr(action, "play_tags", ()))
        action_conflicts = set(getattr(action, "play_conflicts", ()))

        if method_tags & action_conflicts:
            raise ValueError(
                f"Selected play method '{selected_method.method}' cannot be combined with {action.__class__.__name__}"
            )
        if method_conflicts & action_tags:
            raise ValueError(
                f"Play effect {action.__class__.__name__} cannot be combined with method '{selected_method.method}'"
            )

        timing = getattr(action, "play_timing", "post_place")
        if timing == "pre_place":
            pre_place_actions.append(action)
        elif timing == "post_place":
            post_place_actions.append(action)
        else:
            raise ValueError(
                f"Unknown play timing '{timing}' on {action.__class__.__name__}"
            )

    return PlayPlan(
        card=card,
        selected_method=selected_method,
        pre_place_actions=tuple(pre_place_actions),
        post_place_actions=tuple(post_place_actions),
    )
