from exchange import Event


@Event.register_event
class EventScheduleTo(Event):

    def __init__(self, time, receiver, event):
        self.time = time
        self.receiver = receiver
        if isinstance(event, Event):
            self.event = event.__dict__
            self.event["name"] = type(event).__name__
        elif isinstance(event, dict):
            self.event = event
        else:
            raise TypeError

    def get_event(self):
        event = self.event.copy()
        event_name = event["name"]
        del(event["name"])
        if event_name in Event.registered_events:
            return Event.registered_events[event_name](**event)
        else:
            return Event(event_name)


@Event.register_event
class ClearScheduledTasks(Event):
    def __init__(self):
        pass
