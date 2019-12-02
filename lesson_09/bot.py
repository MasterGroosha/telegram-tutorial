# -*- coding: utf-8 -*-

import telebot
from telebot import types

bot = telebot.TeleBot("Токен вашего бота")


@bot.message_handler(commands=["geophone"])
def geophone(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
    button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard.add(button_phone, button_geo)
    bot.send_message(message.chat.id,
                     text="Отправь мне свой номер телефона или поделись местоположением, жалкий человечишка!",
                     reply_markup=keyboard)


@bot.message_handler(func=lambda message: True)
def any_message(message):
    bot.reply_to(message, "Сам {!s}".format(message.text))


@bot.edited_message_handler(func=lambda message: True)
def edit_message(message):
    bot.edit_message_text(chat_id=message.chat.id,
                          text="Сам {!s}".format(message.text),
                          message_id=message.message_id + 1)


@bot.inline_handler(func=lambda query: True)
def inline_mode(query):
    capibara1 = types.InlineQueryResultCachedPhoto(
        id="1",
        photo_file_id="AgADAgAD6rMxGyBnGwABgBmcoHgy6IENAAQSYK_1gyoAAU-5aQACAg",
        caption="Это капибара №1"
    )
    capibara2 = types.InlineQueryResultCachedPhoto(
        id="2",
        photo_file_id="AgADAgAD67MxGyBnGwABCvqPIYxMNHENAAS51HjO88y_Z0ffAQABAg",
        caption="Это капибара №2"
    )
    bot.answer_inline_query(query.id, [capibara1, capibara2])


if __name__ == "__main__":
    bot.infinity_polling()
