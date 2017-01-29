import exchange.Event as Event


class EventTurnOn(Event):
    def __init__(self):
        super().__init__()


class EventTurnOff(Event):
    def __init__(self):
        super().__init__()


class EventTurnSlowly(Event):
    def __init__(self, turn_to, time_sec=180):
        super().__init__()
        self.turn_to = turn_to
        self.time_sec = time_sec
