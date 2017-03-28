import time
import settings
from backend.presencenotify.router_scraper import RouterScraper
from exchange import Messenger, PresenceNotifierEvents
from exchange.json_generic import JSONSerializibleMixin


class User(JSONSerializibleMixin):
    def __init__(self, name=None):
        self.name = name
        self.devices = {}

    def add_device(self, name, mac_addr):
        self.devices[mac_addr] = name

    def remove_device(self, mac_addr):
        del(self.devices[mac_addr])


class UserManager(object):
    def __init__(self):
        self.users = []  # TODO: читать пользователей из json файла

    def add_user(self, user):
        if isinstance(user, User):
            self.users.append(user)
        else:
            raise TypeError
        # TODO после добавления пользователя, сохранять в файл

    def find_user_by_device_mac(self, mac_addr):
        for user in self.users:
            if mac_addr in user.devices:
                return user
        return False

    def to_file(self):
        pass  # TODO: сохранение в json

    def from_file(self):
        pass  # TODO: чтение из json


class PresenceNotifier(object):
    def __init__(self):
        self.user_manager = UserManager()
        self.wireless_devices = RouterScraper.get_wireless_clients()

    def process_devices(self, connected_devices, disconnected_devices):
        connected_users = []
        connected_unknown_devices = []
        for device in connected_devices:
            user = self.user_manager.find_user_by_device_mac(device.mac_addr)
            if user:
                connected_users.append(user)
            else:
                connected_unknown_devices.append(device)

        disconnected_users = []
        disconnected_unknown_devices = []
        for device in disconnected_devices:
            user = self.user_manager.find_user_by_device_mac(device.mac_addr)
            if user:
                disconnected_users.append(user)
            else:
                disconnected_unknown_devices.append(device)

        return connected_users, connected_unknown_devices, disconnected_users, disconnected_unknown_devices

    def check(self):
        wireless_devices = RouterScraper.get_wireless_clients()
        connected_devices = []
        disconnected_devices = []
        if self.wireless_devices != wireless_devices:
            connected_devices = list(set(wireless_devices) - set(self.wireless_devices))
            disconnected_devices = list(set(self.wireless_devices) - set(wireless_devices))
        self.wireless_devices = wireless_devices
        return connected_devices, disconnected_devices

    def run(self):
        messenger = Messenger(settings.RABBITMQ_HOST)
        while True:
            connected_devices, disconnected_devices = self.check()
            if len(connected_devices) or len(disconnected_devices):
                result = self.process_devices(connected_devices, disconnected_devices)
                messenger.publish_to_frontend(PresenceNotifierEvents.EventNotify(*result))
            time.sleep(settings.PRESENCE_NOTIFIER_CHECK_INTERVAL)


if __name__ == "__main__":
    pn = PresenceNotifier()
    pn.run()
