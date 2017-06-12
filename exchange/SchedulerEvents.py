from exchange import Event


class EventScheduleTo(Event):

    def __init__(self, time=None, receiver=None, event=None):
        self.time = time
        self.receiver = receiver
        self.event = event

    def get_event(self):
        return self.event


class ClearScheduledTasks(Event):
    def __init__(self):
        pass
