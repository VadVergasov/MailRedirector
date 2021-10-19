import email
import ujson as json
import logging
import os

import html2text
import imapclient
import telebot

import config

logging.basicConfig(
    filename="mail.log",
    format="%(asctime)s - %(levelname)s: %(message)s",
    level=logging.INFO,
)

BOT = telebot.TeleBot(config.TOKEN)
SERVER = imapclient.IMAPClient(config.SERVER, port=993, ssl=True)
SERVER.login(config.LOGIN, config.PASSWORD)
SERVER.select_folder("INBOX")

INFO = json.load(open("config.json", "r", encoding="utf8"))

MESSAGES = SERVER.search("ALL")
for uid, data in SERVER.fetch(MESSAGES, "RFC822").items():
    if uid <= int(INFO["latest"]):
        continue
    logging.info("Fetching unseen messages: " + str(uid))
    logging.info("Lastest sended message is: " + str(INFO["latest"]))
    email_message = email.message_from_bytes(data[b"RFC822"])
    title_text, title_encoding = email.header.decode_header(
        email_message.get("Subject")
    )[0]
    from_text, from_encoding = email.header.decode_header(email_message.get("From"))[0]
    if not isinstance(title_text, str):
        title_text = title_text.decode(title_encoding)
    if not isinstance(from_text, str):
        from_text = from_text.decode(from_encoding)
    title_text = title_text.replace("*", "*\\**")
    title_text = title_text.replace("_", "\\_")
    title_text = title_text.replace("`", "\\`")
    title_text = title_text.replace("[", "\\[")
    from_text = from_text.replace("*", "\\*")
    from_text = from_text.replace("_", "_\\__")
    from_text = from_text.replace("`", "\\`")
    from_text = from_text.replace("[", "\\[")
    message_text = "_" + from_text + "_\n*" + title_text + "*\n"

    for part in email_message.walk():
        if part.get_content_type() == "text/plain":
            body_text = part.get_payload(decode=True).decode("utf8")
            body_text = body_text.replace("`", "\\`")
            body_text = body_text.replace("[", "\\[")
            message_text += "```\n" + body_text + "\n```"
            break
        if part.get_content_type() == "text/html":
            body_text = ""
            body_text = html2text.html2text(
                part.get_payload(decode=True).decode("utf8")
            )
            body_text = body_text.replace("`", "\\`")
            body_text = body_text.replace("[", "\\[")
            message_text += "```\n" + body_text + "\n```"
        else:
            print(part.get_content_type())

    splitted_text = []
    attachments = []
    logging.info("Getting attachments")
    for part in email_message.walk():
        if part.get_content_maintype() == "multipart":
            continue
        if part.get("Content-Disposition") is None:
            continue

        filename, filename_encoding = email.header.decode_header(part.get_filename())[0]
        if not isinstance(filename, str):
            filename = filename.decode(filename_encoding)

        att_path = os.path.join(INFO["folder"] + "/tmp", filename)
        if not os.path.isfile(att_path):
            fp = open(att_path, "wb")
            fp.write(part.get_payload(decode=True))
            fp.close()
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
            attachments.append(telebot.types.InputMediaDocument(open(att_path, "rb")))
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
    INFO["latest"] = uid
    with open("config.json", "w", encoding="utf8") as fp:
        json.dump(INFO, fp, ensure_ascii=False)


SERVER.logout()
