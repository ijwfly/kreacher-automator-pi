class Event(object):
	def __init__(self, sender, reciever, event_name, event_data):
		self.reciever = reciever
		self.sender = sender
		self.event_name = event_name
		self.event_data = event_data


class EventManager(object):
	def __init__(self):
		self.ports = []

	def __manage_event(self, event):
		for port in self.ports:
			if (port.port_id == event.reciever):
				port.send_event(event)

	def create_port(self, port_id):
		port = EventPort(self, port_id)
		self.ports.append(port)
		return port


class EventPort(EventManager):
	def __init__(self, event_manager, port_id):
		self.event_manager = event_manager
		self.port_id = port_id

	def send_event(self, reciever, event_name, event_data):
		self.event_manager.__manage_event(Event(self.port_id, reciever, event_name, event_data))
