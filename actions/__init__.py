"""Action package.

Keep this module import-light to avoid circular import chains.
Import concrete symbols from submodules, for example:
- from actions.cards import action_play_card
- from actions.locations import action_place_worker
"""

__all__: list[str] = []
