import exchange.Event as Event


class EventSuccess(Event):
    def __init__(self):
        super().__init__()


class EventFailure(Event):
    def __init__(self, message=None):
        super().__init__()
        self.message = message


class EventInfo(Event):
    def __init__(self, info):
        super().__init__()
        self.info = info_message
