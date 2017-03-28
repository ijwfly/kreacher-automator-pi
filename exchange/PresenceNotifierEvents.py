import backend.presencenotify # needed for json_generic
from exchange import Event


# Backend -> Frontend Events
class EventNotify(Event):
    def __init__(self, connected_users=None, connected_unknown_devices=None, disconnected_users=None, disconnected_unknown_devices=None):
        self.connected_users = connected_users
        self.connected_unknown_devices = connected_unknown_devices
        self.disconnected_users = disconnected_users
        self.disconnected_unknown_devices = disconnected_unknown_devices


# Frontend -> Backend Events
class EventCheckConnectedUsers(Event):
    pass
