import time
import logging
import schedule
import settings
from exchange import Messenger, Event

messenger = Messenger(settings.RABBITMQ_HOST)


def do_scheduled_action(receiver, event):
    def action():
        messenger.publish_to_backend(receiver, event)
    return action


def handle_event(event):
    if event.name == "scheduleTaskTime":
        if event.data:
            schedule.every().day.at(event.data["time"]).do(
                do_scheduled_action(event.data["receiver"], Event(**event.data["event"]))
            )
        print("event is set")
    elif event.name == "resetAllScheduledTasks":
        schedule.clear()
        print("all events are cleared")


if __name__ == "__main__":
    messenger.subscribe_backend("scheduler", handle_event)
    messenger.wait_for_messages()

    try:
        while True:
            schedule.run_pending()
            time.sleep(10)
    except Exception as exception:
        logging.error("scheduler exception: " + exception)
