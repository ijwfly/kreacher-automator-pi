import telebot
import settings
import logging
from exchange import Messenger, Event

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN, skip_pending=True)


def handle_event(event):
    print("there is an event O_O")
    if event.name == "helloWorld":
        bot.send_message(settings.TELEGRAM_ADMIN_ID, "hello, world!")


if __name__ == "__main__":
    messenger = Messenger(settings.RABBITMQ_HOST)
    messenger.subscribe_frontend(handle_event)

    messenger.wait_for_messages(False)
    try:
        bot.polling()
    except Exception as exception:
        logging.error("pyTelegramBotApi exception: " + exception)

