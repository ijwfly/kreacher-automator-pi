import logging
import settings

if __name__ == "__main__":
    logging.basicConfig(filename=settings.RUN_DIR + "/kreacher.log", level=logging.WARNING)
