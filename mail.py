import logging
import os

import html2text
from imap_tools import MailBox, AND
import telebot
import ujson as json

import config

logging.basicConfig(
    filename="mail.log",
    format="%(asctime)s - %(levelname)s: %(message)s",
    level=logging.INFO,
    encoding="utf8",
)

BOT = telebot.TeleBot(config.TOKEN)

with open("config.json", "r", encoding="utf8") as fp:
    INFO = json.load(fp)

with MailBox(config.SERVER).login(
    config.LOGIN, config.PASSWORD, initial_folder="Inbox"
) as mailbox:
    for msg in mailbox.fetch(AND(all=True), bulk=True):
        if int(msg.uid) <= int(INFO["latest"]):
            continue
        logging.info("Fetching unseen messages: " + str(msg.uid))
        logging.info("Lastest sended message is: " + str(INFO["latest"]))
        title_text = msg.subject
        from_text = msg.from_

        # Adding symbols for correct MARKDOWN format
        title_text = title_text.replace("*", "*\\**")
        title_text = title_text.replace("_", "\\_")
        title_text = title_text.replace("`", "\\`")
        title_text = title_text.replace("[", "\\[")
        from_text = from_text.replace("*", "\\*")
        from_text = from_text.replace("_", "_\\__")
        from_text = from_text.replace("`", "\\`")
        from_text = from_text.replace("[", "\\[")

        # Text of message
        message_text = "_" + from_text + "_\n*" + title_text + "*\n"
        if not msg.text == "":
            message_text += "```\n" + msg.text + "\n```"
        else:
            message_text += "```\n" + html2text.html2text(msg.html) + "\n```"

        splitted_text = []
        attachments = []
        logging.info("Getting attachments")
        for att in msg.attachments:
            folder = os.path.join(os.path.normpath(INFO["folder"]), "tmp")
            if not os.path.isdir(folder):
                os.mkdir(folder)

            att_path = os.path.join(folder, att.filename)
            with open(att_path, "wb") as fp:
                fp.write(att.payload)

            if len(attachments) == 0:
                splitted_text = telebot.util.smart_split(
                    message_text, chars_per_string=1000
                )
                if len(splitted_text) > 1:
                    attachments.append(
                        telebot.types.InputMediaDocument(
                            open(att_path, "rb"),
                            caption=splitted_text[0] + "```",
                            parse_mode="MARKDOWN",
                        )
                    )
                else:
                    attachments.append(
                        telebot.types.InputMediaDocument(
                            open(att_path, "rb"),
                            caption=splitted_text[0],
                            parse_mode="MARKDOWN",
                        )
                    )
            else:
                attachments.append(
                    telebot.types.InputMediaDocument(open(att_path, "rb"))
                )
        logging.info(message_text)
        logging.info(len(attachments))
        logging.info("Sending message")
        for chat_id in INFO["chats"]:
            if len(attachments) == 0:
                splitted_text = telebot.util.smart_split(
                    message_text, chars_per_string=4000
                )
                if len(splitted_text) > 1:
                    BOT.send_message(
                        chat_id, splitted_text[0] + "````", parse_mode="MARKDOWN"
                    )
                else:
                    BOT.send_message(chat_id, splitted_text[0], parse_mode="MARKDOWN")
            else:
                BOT.send_media_group(chat_id, attachments)
            for text in splitted_text[1:-1]:
                BOT.send_message(chat_id, "```\n" + text + "```", parse_mode="MARKDOWN")
            if len(splitted_text) > 1:
                BOT.send_message(
                    chat_id, "```\n" + splitted_text[-1], parse_mode="MARKDOWN"
                )
        INFO["latest"] = int(msg.uid)
        with open("config.json", "w", encoding="utf8") as fp:
            json.dump(INFO, fp, ensure_ascii=False)
