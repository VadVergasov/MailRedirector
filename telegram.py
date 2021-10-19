import telebot
import ujson as json

import logging
import config

BOT = telebot.TeleBot(config.TOKEN)
logging.basicConfig(
    filename="telegram.log",
    format="%(asctime)s - %(levelname)s: %(message)s",
    level=logging.INFO,
)

with open("config.json", "r", encoding="utf8") as fp:
    DATABASE = json.load(fp)


def update_database():
    with open("config.json", "w", encoding="utf8") as fp:
        json.dump(DATABASE, fp, ensure_ascii=False)


@BOT.message_handler(commands=["start", "help"])
def start_private(message):
    if message.chat.id not in DATABASE["chats"]:
        DATABASE["chats"].append(message.chat.id)
        update_database()
    BOT.reply_to(message, config.HELP)


@BOT.channel_post_handler(commands=["start", "help"])
def start_channel(message):
    if message.chat.id not in DATABASE["chats"]:
        DATABASE["chats"].append(message.chat.id)
        update_database()
    BOT.reply_to(message, config.HELP)


@BOT.message_handler(commands=["stop"])
def stop_private(message):
    if message.chat.id in DATABASE["chats"]:
        DATABASE["chats"].remove(message.chat.id)
        update_database()
    BOT.reply_to(message, config.STOP)


@BOT.channel_post_handler(commands=["stop"])
def stop_channel(message):
    if message.chat.id in DATABASE["chats"]:
        DATABASE["chats"].remove(message.chat.id)
        update_database()
    BOT.reply_to(message, config.STOP)


commands = []
for command in config.COMMANDS.keys():
    commands.append(telebot.types.BotCommand(command, config.COMMANDS[command]))

BOT.set_my_commands(commands)

BOT.polling(non_stop=True)
