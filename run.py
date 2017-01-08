import sys
import time
import logging
import settings

from backend.bulb import BulbProcessor

if __name__ == "__main__":
	logging.basicConfig(filename=settings.RUN_DIR + "/kreacher.log", level=logging.WARNING)

	bulb = BulbProcessor(settings.MAGIC_BULB_ADDR)
	bulb.turn_on()
	time.sleep(5)
	bulb.turn_off()
