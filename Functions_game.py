# The following actions should be modeled:
    # Get possible cards to play (from hand, from meadow)
    # Get possible locations to place worker

# A player can perform three main actions
# A function should be created to check which actions are possible
# A function should be created to choose which action to execute
# The three main actions are:
    # Place worker (choose location)
    # Play card (Choose card)
    # Prepare for season


def prepare_for_season(deck, discardpile, meadow, player):
    # Check the current season
    # Check the number of workers on hand
    # Execute actions from cards
    # Execute actions from season (spring: add 1 worker + execute green, summer: add 1 worker + draw 2 cards from meadow, autumn: add 2 workers + execture green)
    # Bring back workers
    return deck, discardpile, meadow, player