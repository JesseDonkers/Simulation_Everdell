class Location:
    """
    Basic event
    Special event
    Basic location
    Forest location
    Haven
    Journey
    Destination card
    """
    def __init__(self):
        self.exclusive = False
        self.occupied = False
        self.open = False # Attribute for destination cards
        self.workers = 0
        self.maxworkers = 0

