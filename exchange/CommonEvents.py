from exchange import Event


@Event.register_event
class EventSuccess(Event):
    def __init__(self):
        super().__init__()


@Event.register_event
class EventFailure(Event):
    def __init__(self, message=None):
        super().__init__()
        self.message = message


@Event.register_event
class EventInfo(Event):
    def __init__(self, info):
        data = {"info": info}
        super().__init__(info)
