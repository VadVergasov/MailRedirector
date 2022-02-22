import logging

import telebot
import ujson as json

import config

BOT = telebot.TeleBot(config.TOKEN)
logging.basicConfig(
    filename="telegram.log",
    format="%(asctime)s - %(levelname)s - %(funcName)s() - %(lineno)d: %(message)s",
    level=logging.INFO,
    encoding="utf8",
)

with open("config.json", "r", encoding="utf8") as fp:
    DATABASE = json.load(fp)


def check_for_credentials(message):
    """
    Check if message is answer to login request message.
    """
    if message.text is not None and len(message.text.split(" ")) == 2:
        try:
            return message.reply_to_message.text == config.LOGIN
        except AttributeError:
            return False
    return False


def update_database():
    with open("config.json", "w", encoding="utf8") as fp:
        json.dump(DATABASE, fp, ensure_ascii=False)


@BOT.message_handler(func=check_for_credentials)
def login(message):
    if str(message.chat.id) not in DATABASE.keys():
        DATABASE[str(message.chat.id)] = {
            "latest": 0,
            "password": message.text.split(" ")[1],
            "login": message.text.split(" ")[0],
        }
        update_database()
    BOT.reply_to(message, config.HELP)


@BOT.channel_post_handler(func=check_for_credentials)
def login_channel(message):
    if str(message.chat.id) not in DATABASE.keys():
        DATABASE[str(message.chat.id)] = {
            "latest": 0,
            "password": message.text.split(" ")[1],
            "login": message.text.split(" ")[0],
        }
        update_database()
    BOT.reply_to(message, config.HELP)


@BOT.message_handler(commands=["start", "help"])
def start_private(message):
    BOT.reply_to(message, config.LOGIN)


@BOT.channel_post_handler(commands=["start", "help"])
def start_channel(message):
    BOT.reply_to(message, config.LOGIN)


@BOT.message_handler(commands=["stop"])
def stop_private(message):
    if str(message.chat.id) in DATABASE.keys():
        DATABASE.remove(str(message.chat.id))
        update_database()
    BOT.reply_to(message, config.STOP)


@BOT.channel_post_handler(commands=["stop"])
def stop_channel(message):
    if str(message.chat.id) in DATABASE.keys():
        DATABASE.remove(str(message.chat.id))
        update_database()
    BOT.reply_to(message, config.STOP)


commands = []
for command, info in config.COMMANDS.items():
    commands.append(telebot.types.BotCommand(command, info))

BOT.set_my_commands(commands)

BOT.remove_webhook()
BOT.polling(non_stop=True)
