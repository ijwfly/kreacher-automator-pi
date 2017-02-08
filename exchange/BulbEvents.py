from exchange import Event


@Event.register_event
class EventTurnOn(Event):
    def __init__(self):
        super().__init__()


@Event.register_event
class EventTurnOff(Event):
    def __init__(self):
        super().__init__()


@Event.register_event
class EventTurnSlowly(Event):
    def __init__(self, turn_to, time_sec=180):
        super().__init__()
        self.turn_to = turn_to
        self.time_sec = time_sec
