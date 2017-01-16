import threading
import time
import schedule
from lib.magicbulbcontrol import MagicBulb
import lib.eventmanager as em


# TODO: save current bulb state
class BulbProcessor(em.Subscriber):

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

    # alarm_time - "HH:mm", ex: "13:24"
    def set_alarm(self, alarm_time):
        schedule.every().day.at(alarm_time).do(self.alarm)

    def reset_alarms(self):
        schedule.clear()

    def run(self):
        while true:
            schedule.run_pending()
            time.sleep(10)

