import time
import logging
import schedule
import settings
from exchange import Messenger, SchedulerEvents, CommonEvents, BulbEvents

messenger = Messenger(settings.RABBITMQ_HOST)


def do_scheduled_action(receiver, event):
    def action():
        messenger.publish_to_backend(receiver, event)
    return action


def handle_event(event):
    if event.is_an(SchedulerEvents.EventScheduleTo):
        schedule.every().day.at(event.time).do(
            do_scheduled_action(event.receiver, event.get_event())
        )
        return CommonEvents.EventSuccess()
    elif event.is_an(SchedulerEvents.ClearScheduledTasks):
        schedule.clear()
        return CommonEvents.EventSuccess()


def run():
    messenger.subscribe_backend("scheduler", handle_event)
    messenger.wait_for_messages()

    try:
        while True:
            schedule.run_pending()
            time.sleep(10)
    except Exception as exception:
        logging.error("scheduler exception: " + exception)

if __name__ == "__main__":
    run()
