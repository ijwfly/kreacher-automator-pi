import telebot
import settings
import logging
from exchange import Messenger, Event

commands = {
    "lightOn": "Включи свет",
    "lightOff": "Выключи свет",
    "setAlarm": "Установи будильник",
    "resetAlarms": "Сбрось все будильники",
    "sunrise": "Время рассвета",
    "sunset": "Время заката",
    "mopidyOn": "Включи mopidy",
    "mopidyOff": "Выключи mopidy",
    "tvOn": "Включи телевизор",
    "tvOff": "Выключи телевизор",
}

answers = {
    "onStart": "Кикимер живет, чтобы служить благородному дому Блеков.",
    "imSorry": "Простите, господин, произошла какая-то ошибка...",
    "alarmIsSet": "Будильник установлен, господин!",
    "alarmsAreReset": "Все будильники сброшены, господин!",
    "notImplemented": "Простите, но я пока не научился таким фокусам"
}

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN, skip_pending=True)
messenger = Messenger(settings.RABBITMQ_HOST)


def get_menu():
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    button_light_on = telebot.types.KeyboardButton(commands["lightOn"])
    button_light_off = telebot.types.KeyboardButton(commands["lightOff"])
    button_sunrise = telebot.types.KeyboardButton(commands["sunrise"])
    button_sunset = telebot.types.KeyboardButton(commands["sunset"])
    button_set_alarm = telebot.types.KeyboardButton(commands["setAlarm"])
    button_reset_alarms = telebot.types.KeyboardButton(commands["resetAlarms"])

    button_mopidy_on = telebot.types.KeyboardButton(commands["mopidyOn"])
    button_mopidy_off = telebot.types.KeyboardButton(commands["mopidyOff"])
    button_tv_on = telebot.types.KeyboardButton(commands["tvOn"])
    button_tv_off = telebot.types.KeyboardButton(commands["tvOff"])

    markup.add(button_light_on, button_light_off,
               button_sunrise, button_sunset,
               button_set_alarm, button_reset_alarms,
               button_mopidy_on, button_mopidy_off,
               button_tv_on, button_tv_off)
    return markup


def is_command(command_name):
    def telebot_handler(message):
        return message.text == commands[command_name]
    return telebot_handler


#TODO: пробрасывать сообщения об успехе/провале обратно
@bot.message_handler(commands=["start"])
def on_start(message):
    bot.reply_to(message, answers["onStart"], reply_markup=get_menu())


@bot.message_handler(func=is_command("lightOn"))
def turn_light_on(message):
    messenger.publish_to_backend("bulb", Event("turnOn"))


@bot.message_handler(func=is_command("lightOff"))
def turn_light_off(message):
    messenger.publish_to_backend("bulb", Event("turnOff"))


@bot.message_handler(func=is_command("sunrise"))
def turn_light_on_slowly(message):
    messenger.publish_to_backend("bulb", Event("turnOnSlowly"))


@bot.message_handler(func=is_command("sunset"))
def turn_light_off_slowly(message):
    messenger.publish_to_backend("bulb", Event("turnOffSlowly"))


@bot.message_handler(func=is_command("setAlarm"))
def set_alarm(message):
    msg = bot.reply_to(message, "Во сколько начинать рассвет для господина?")

    def process_alarm(message):
        alarm_time = message.text
        alarm_event = Event("alarm")
        event = Event("scheduleTaskTime", data={
            "time": alarm_time,
            "receiver": "bulb",
            "event": alarm_event
        })
        messenger.publish_to_backend("scheduler", event)
        # TODO: проверять успешность
        bot.reply_to(message, answers["alarmIsSet"])

    bot.register_next_step_handler(msg, process_alarm)


@bot.message_handler(func=is_command("resetAlarms"))
def reset_alarms(message):
    messenger.publish_to_backend("scheduler", Event("resetAllScheduledTasks"))
    bot.reply_to(message, answers["alarmsAreReset"])

# TODO: не реализованные
@bot.message_handler(func=is_command("mopidyOn"))
def mopidy_on(message):
    # subprocess.call(['nohup mopidy &'], shell=True)
    # bot.reply_to(message, "Mopidy запущен, господин!")
    bot.reply_to(message, answers["notImplemented"])


@bot.message_handler(func=is_command("mopidyOff"))
def mopidy_off(message):
    # subprocess.call(['pkill mopidy'], shell=True)
    # bot.reply_to(message, "Mopidy остановлен, господин!")
    bot.reply_to(message, answers["notImplemented"])


@bot.message_handler(func=is_command("tvOn"))
def tv_on(message):
    # subprocess.call(['/home/pi/useful_scripts/control_tv/turn_on.sh'], shell=True)
    # bot.reply_to(message, "Телевизор включен, господин!")
    bot.reply_to(message, answers["notImplemented"])


@bot.message_handler(func=is_command("tvOff"))
def tv_off(message):
    # subprocess.call(['/home/pi/useful_scripts/control_tv/turn_off.sh'], shell=True)
    # bot.reply_to(message, "Телевизор выключен, господин!")
    bot.reply_to(message, answers["notImplemented"])


def handle_event(event):
    if event.name == "adminNotify":
        if event.data:
            bot.send_message(settings.TELEGRAM_ADMIN_ID, event.data)
        else:
            bot.send_message(settings.TELEGRAM_ADMIN_ID, "Уведомление!")


if __name__ == "__main__":
    try:
        messenger.subscribe_frontend(handle_event)
        messenger.wait_for_messages()
        print("polling started")
        bot.polling()
    except Exception as exception:
        logging.error("telegram frontend exception: " + exception)
