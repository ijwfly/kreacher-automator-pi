class Event(object):
    def __init__(self, event_name, event_data=None):
        self.name = event_name
        self.data = event_data


class Subscriber(object):
    def __init__(self):
        self.event_manager = None
        self.process_event = None

    def subscribe(self, event_manager, callback):
        self.event_manager = event_manager
        self.process_event = callback

    def handle_event(self, event):
        raise "handle event is not implemented"


class EventManager(object):
    def __init__(self):
        self.fronts = []
        self.backs = []

    def subscribe_front(self, front):
        self.fronts.append(front)
        front.subscribe(self, self.send_to_back)

    def subscribe_back(self, back):
        self.backs.append(back)
        back.subscribe(self, self.send_to_front)

    def send_to_front(self, event):
        for front in self.fronts:
            front.handle_event(event)

    def send_to_back(self, event):
        for back in self.backs:
            back.handle_event(event)
