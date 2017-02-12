from exchange import Event


@Event.register_event
class EventTurnMopidyOn(Event):
    def __init__(self):
        pass


@Event.register_event
class EventTurnMopidyOff(Event):
    def __init__(self):
        pass


@Event.register_event
class EventTurnTvOn(Event):
    def __init__(self):
        pass


@Event.register_event
class EventTurnTvOff(Event):
    def __init__(self):
        pass


@Event.register_event
class EventForceTvSource(Event):
    def __init__(self):
        pass
