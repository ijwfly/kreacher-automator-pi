from exchange import Event


# Backend -> Frontend Events
@Event.register_event
class EventNotify(Event):
    def __init__(self, connected_users, connected_unknown_devices, disconnected_users, disconnected_unknown_devices):
        self.connected_users = connected_users
        self.connected_unknown_devices = connected_unknown_devices
        self.disconnected_users = disconnected_users
        self.disconnected_unknown_devices = disconnected_unknown_devices


# Frontend -> Backend Events
@Event.register_event
class EventCheckConnectedUsers(Event):
    pass
