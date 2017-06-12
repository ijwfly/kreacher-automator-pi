import threading
import time
import settings
from lib.magicbulbcontrol import MagicBulb
from exchange import Messenger, BulbEvents, CommonEvents


# TODO: save current bulb state
class BulbProcessor(object):

    def __init__(self, bulb_addr):
        self.in_use = threading.Event()
        self.bulb = MagicBulb(bulb_addr)

    def handle_event(self, event):
        try:
            if event.is_an(BulbEvents.EventTurnOn):
                self.turn_on()
                return CommonEvents.EventSuccess()
            elif event.is_an(BulbEvents.EventTurnOff):
                self.turn_off()
                return CommonEvents.EventSuccess()
            elif event.is_an(BulbEvents.EventTurnSlowly):
                if event.turn_to:
                    self.turn_on_slowly(event.time_sec)
                else:
                    self.turn_off_slowly(event.time_sec)
                return CommonEvents.EventSuccess()
        except:
            return CommonEvents.EventFailure()

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

    def turn_on_slowly(self, timeout):
        self.in_use.set()
        self.bulb.connect()
        delay = timeout / 255.0
        for brightness in range(0, 255):
            self.bulb.set_color(0, 0, 0, brightness)
            time.sleep(delay)
        self.bulb_set_color(0, 0, 0, 255)
        self.bulb.disconnect()
        self.in_use.clear()

    def turn_off_slowly(self, timeout):
        self.in_use.set()
        self.bulb.connect()
        delay = timeout / 255.0
        for brightness in range(255, 0, -1):
            self.bulb.set_color(0, 0, 0, brightness)
            time.sleep(delay)
        self.bulb.set_color(0, 0, 0, 0)
        self.bulb.disconnect()
        self.in_use.clear()


def run():
    messenger = Messenger(settings.RABBITMQ_HOST)
    bulb = BulbProcessor(settings.MAGIC_BULB_ADDR)

    messenger.subscribe_backend("bulb", bulb.handle_event)
    print("registered!")

    messenger.wait_for_messages(False)


if __name__ == "__main__":
    run()
