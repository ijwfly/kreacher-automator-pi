from exchange import Event


class EventSuccess(Event):
    def __init__(self):
        pass


class EventFailure(Event):
    def __init__(self, message=None):
        self.message = message


class EventInfo(Event):
    def __init__(self, info):
        self.info = info
