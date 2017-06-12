from exchange import Event


class EventTurnOn(Event):
    def __init__(self):
        pass


class EventTurnOff(Event):
    def __init__(self):
        pass


class EventTurnSlowly(Event):
    def __init__(self, turn_to=True, time_sec=180):
        self.turn_to = turn_to
        self.time_sec = time_sec
