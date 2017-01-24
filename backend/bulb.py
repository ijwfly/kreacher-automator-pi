import threading
import time
import settings
from lib.magicbulbcontrol import MagicBulb
from exchange import Messenger, Event


# TODO: save current bulb state
class BulbProcessor(object):

    def __init__(self, bulb_addr):
        self.in_use = threading.Event()
        self.bulb = MagicBulb(bulb_addr)

    def handle_event(self, event):
        if event.name == "turnOn":
            self.turn_on()
        elif event.name == "turnOff":
            self.turn_off()

    def turn_on(self):
        self.in_use.set()
        self.bulb.connect()
        self.bulb.turn_on()
        self.bulb.disconnect()
        self.in_use.clear()

    def turn_off(self):
        self.in_use.set()
        self.bulb.connect()
        self.bulb.turn_off()
        self.bulb.disconnect()
        self.in_use.clear()

    # TODO: add time argument, remove alarm function
    def turn_on_slowly(self):
        self.in_use.set()
        self.bulb.connect()
        for brightness in range(0, 255):
            self.bulb.set_color(0, 0, 0, brightness)
            time.sleep(0.7)
        self.bulb.set_color(0, 0, 0, 255)
        self.bulb.disconnect()
        self.in_use.clear()

    # TODO: add time argument
    def turn_off_slowly(self):
        self.in_use.set()
        self.bulb.connect()
        for brightness in range(255, 0, -1):
            self.bulb.set_color(0, 0, 0, brightness)
            time.sleep(0.7)
        self.bulb.set_color(0, 0, 0, 0)
        self.bulb.disconnect()
        self.in_use.clear()

    def alarm(self):
        self.in_use.set()
        self.bulb.connect()
        for brightness in range(0, 255):
            self.bulb.set_color(0, 0, 0, brightness)
            time.sleep(7.1)
        self.bulb.disconnect()
        self.in_use.clear()


if __name__ == "__main__":
    messenger = Messenger("localhost")
    bulb = BulbProcessor(settings.MAGIC_BULB_ADDR)

    def handle_event(event):
        print("event!")
        print(event.__dict__)
        if event.name == "turnOn":
            bulb.turn_on()
            return Event("success")
        elif event.name == "turnOff":
            bulb.turn_off()
            return Event("success")
        elif event.name == "turnOnSlowly":
            bulb.turn_on_slowly()
        elif event.name == "turnOffSlowly":
            bulb.turn_off_slowly()
        elif event.name == "alarm":
            bulb.alarm()

    print("registered!")

    messenger.subscribe_backend("bulb", handle_event)
    messenger.wait_for_messages(False)
