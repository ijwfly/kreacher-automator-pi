from exchange import Event


@Event.register_event
class EventSuccess(Event):
    def __init__(self):
        pass


@Event.register_event
class EventFailure(Event):
    def __init__(self, message=None):
        self.message = message


@Event.register_event
class EventInfo(Event):
    def __init__(self, info):
        self.info = info
