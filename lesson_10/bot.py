# -*- coding: utf-8 -*-

import telebot
from time import time


bot = telebot.TeleBot("Токен вашего бота")

GROUP_ID = -10012345  # ID вашей группы

strings = {
    "ru": {
        "ro_msg": "Вам запрещено отправлять сюда сообщения в течение 10 минут."
    },
    "en": {
        "ro_msg": "You're not allowed to send messages here for 10 minutes."
    }
}


def get_language(lang_code):
    # Иногда language_code может быть None
    if not lang_code:
        return "en"
    if "-" in lang_code:
        lang_code = lang_code.split("-")[0]
    if lang_code == "ru":
        return "ru"
    else:
        return "en"


# Удаляем сообщения с ссылками
@bot.message_handler(func=lambda message: message.entities is not None and message.chat.id == GROUP_ID)
def delete_links(message):
    for entity in message.entities:
        if entity.type in ["url", "text_link"]:
            bot.delete_message(message.chat.id, message.message_id)
        else:
            return


restricted_messages = ["я веган", "i am vegan"]


# Выдаём Read-only за определённые фразы
@bot.message_handler(func=lambda message: message.text and message.text.lower() in restricted_messages and message.chat.id == GROUP_ID)
def set_ro(message):
    print(message.from_user.language_code)
    bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=time()+600)
    bot.send_message(message.chat.id, strings.get(get_language(message.from_user.language_code)).get("ro_msg"),
                     reply_to_message_id=message.message_id)


if __name__ == "__main__":
    bot.infinity_polling()
