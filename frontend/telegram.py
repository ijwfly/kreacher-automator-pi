import telebot
import settings
import logging
from exchange import Messenger
from exchange import CommonEvents, BulbEvents, SchedulerEvents, SystemCmdEvents

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
    "forceTvSource": "Переключи телевизор"
}

answers = {
    "onStart": "Кикимер живет, чтобы служить благородному дому Блеков.",
    "lightIsOn": "Свет включен, господин!",
    "lightIsOff": "Свет выключен, господин!",
    "imSorry": "Простите, господин, произошла какая-то ошибка...",
    "alarmIsSet": "Будильник установлен, господин!",
    "alarmsAreReset": "Все будильники сброшены, господин!",
    "notImplemented": "Простите, но я пока не научился таким фокусам",
    "sunRisen": "Солнце уже высоко, господин",
    "sunSet": "Крепкого сна, господин",
    "mopidyIsOn": "Mopidy включен, господин",
    "mopidyIsOff": "Mopidy выключен, господин",
    "tvIsOn": "Телевизор включен, господин",
    "tvIsOff": "Телевизор выключен, господин",
    "tvSourceForced": "Канал переключен на малину, господин"
}

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN, skip_pending=True)
messenger = Messenger(settings.RABBITMQ_HOST)


def check_result(message, event, success_answer, fail_answer=answers["imSorry"]):
    if event.is_an(CommonEvents.EventSuccess):
        bot.reply_to(message, success_answer)
    else:
        bot.reply_to(message, fail_answer)


def get_menu():
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)

    button = telebot.types.KeyboardButton
    button_light_on = button(commands["lightOn"])
    button_light_off = button(commands["lightOff"])
    button_sunrise = button(commands["sunrise"])
    button_sunset = button(commands["sunset"])
    button_set_alarm = button(commands["setAlarm"])
    button_reset_alarms = button(commands["resetAlarms"])

    button_mopidy_on = button(commands["mopidyOn"])
    button_mopidy_off = button(commands["mopidyOff"])
    button_tv_on = button(commands["tvOn"])
    button_tv_off = button(commands["tvOff"])
    button_force_tv = button(commands["forceTvSource"])

    markup.add(button_light_on, button_light_off,
               button_sunrise, button_sunset,
               button_set_alarm, button_reset_alarms,
               button_mopidy_on, button_mopidy_off,
               button_tv_on, button_tv_off,
               button_force_tv)

    return markup


def is_command(command_name):
    def telebot_handler(message):
        return message.text == commands[command_name]
    return telebot_handler


@bot.message_handler(commands=["start"])
def on_start(message):
    bot.reply_to(message, answers["onStart"], reply_markup=get_menu())


@bot.message_handler(func=is_command("lightOn"))
def turn_light_on(message):
    messenger.publish_to_backend("bulb", BulbEvents.EventTurnOn(),
                                 lambda event: check_result(message, event, answers["lightIsOn"]))


@bot.message_handler(func=is_command("lightOff"))
def turn_light_off(message):
    messenger.publish_to_backend("bulb", BulbEvents.EventTurnOff(),
                                 lambda event: check_result(message, event, answers["lightIsOff"]))


@bot.message_handler(func=is_command("sunrise"))
def turn_light_on_slowly(message):
    messenger.publish_to_backend("bulb", BulbEvents.EventTurnSlowly(True, 180),
                                 lambda event: check_result(message, event, answers["sunRisen"]))


@bot.message_handler(func=is_command("sunset"))
def turn_light_off_slowly(message):
    messenger.publish_to_backend("bulb", BulbEvents.EventTurnSlowly(False, 180),
                                 lambda event: check_result(message, event, answers["sunSet"]))


@bot.message_handler(func=is_command("setAlarm"))
def set_alarm(message):
    msg = bot.reply_to(message, "Во сколько начинать рассвет для господина?")

    def process_alarm(message):
        alarm_time = message.text
        alarm_event = BulbEvents.EventTurnSlowly(True, 1800)
        scheduler_event = SchedulerEvents.EventScheduleTo(alarm_time, "bulb", alarm_event)
        messenger.publish_to_backend("scheduler", scheduler_event,
                                     lambda event: check_result(message, event, answers["alarmIsSet"]))

    bot.register_next_step_handler(msg, process_alarm)


@bot.message_handler(func=is_command("resetAlarms"))
def reset_alarms(message):
    messenger.publish_to_backend("scheduler", SchedulerEvents.ClearScheduledTasks(),
                                 lambda event: check_result(message, event, answers["imSorry"]))


@bot.message_handler(func=is_command("mopidyOn"))
def mopidy_on(message):
    messenger.publish_to_backend("systemcmd", SystemCmdEvents.EventTurnMopidyOn(),
                                 lambda event: check_result(message, event, answers["mopidyIsOn"]))


@bot.message_handler(func=is_command("mopidyOff"))
def mopidy_off(message):
    messenger.publish_to_backend("systemcmd", SystemCmdEvents.EventTurnMopidyOff(),
                                 lambda event: check_result(message, event, answers["mopidyIsOff"]))


@bot.message_handler(func=is_command("tvOn"))
def tv_on(message):
    messenger.publish_to_backend("systemcmd", SystemCmdEvents.EventTurnTvOn(),
                                 lambda event: check_result(message, event, answers["tvIsOn"]))


@bot.message_handler(func=is_command("tvOff"))
def tv_off(message):
    messenger.publish_to_backend("systemcmd", SystemCmdEvents.EventTurnTvOff(),
                                 lambda event: check_result(message, event, answers["tvIsOff"]))


@bot.message_handler(func=is_command("forceTvSource"))
def tv_off(message):
    messenger.publish_to_backend("systemcmd", SystemCmdEvents.EventForceTvSource(),
                                 lambda event: check_result(message, event, answers["tvSourceForced"]))


def handle_event(event):
    if event.is_an(CommonEvents.EventInfo):
        if event.info:
            bot.send_message(settings.TELEGRAM_ADMIN_ID, event.info)
        else:
            bot.send_message(settings.TELEGRAM_ADMIN_ID, "Меня о чем-то уведомили, господин. Но я не знаю о чем...")


if __name__ == "__main__":
    try:
        messenger.subscribe_frontend(handle_event)
        messenger.wait_for_messages()
        print("polling started")
        bot.polling()
    except Exception as exception:
        logging.error("telegram frontend exception: " + exception)

