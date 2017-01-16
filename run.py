import time
import logging
import settings
from lib.eventmanager import EventManager, Event

from backend.bulb import BulbProcessor

if __name__ == "__main__":
    logging.basicConfig(filename=settings.RUN_DIR + "/kreacher.log", level=logging.WARNING)

    event_manager = EventManager()

    bulb = BulbProcessor(settings.MAGIC_BULB_ADDR)
    event_manager.subscribe_back(bulb)

    event_manager.send_to_back(Event("bulbTurnOn"))
    time.sleep(2)
    event_manager.send_to_back(Event("bulbTurnOff"))
    event_manager.send_to_back(Event("bulbTurnOff"))
    time.sleep(2)
    event_manager.send_to_back(Event("bulbTurnOn"))