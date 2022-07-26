import telebot
import time
import os
import utils
import random
from SQLighter import SQLighter
import config
from telebot import types

bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))

@bot.message_handler(commands=['game'])
def game(message):
    # Подключаемся к БД
    db_worker = SQLighter(config.database_name)
    # Получаем случайную строку из БД
    row = db_worker.select_single(random.randint(1, utils.get_rows_count()))
    # Формируем разметку
    markup = utils.generate_markup(row[2], row[3])
    # Отправляем аудиофайл с вариантами ответа
    bot.send_voice(message.chat.id, row[1], reply_to_message_id=message.message_id, reply_markup=markup)
    # Включаем "игровой режим"
    utils.set_user_game(message.from_user.id, row[2])
    # Отсоединяемся от БД
    db_worker.close()

@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_answer(message):
    # Если функция возвращает None -> Человек не в игре
    answer = utils.get_answer_for_user(message.from_user.id)
    # Как Вы помните, answer может быть либо текст, либо None
    # Если None:
    if not answer:
        bot.send_message(message.chat.id, 'Чтобы начать игру, выберите команду /game', reply_to_message_id=message.message_id)
    else:
        # Уберем клавиатуру с вариантами ответа.
        keyboard_hider = types.ReplyKeyboardRemove()
        # Если ответ правильный/неправильный
        if str(message.text).strip() == str(answer).strip():
            bot.send_message(message.chat.id, 'Верно!', reply_to_message_id=message.message_id, reply_markup=keyboard_hider)
        else:
            bot.send_message(message.chat.id, 'Увы, Вы не угадали. Попробуйте ещё раз!', reply_to_message_id=message.message_id, reply_markup=keyboard_hider)
        # Удаляем юзера из хранилища (игра закончена)
        utils.finish_user_game(message.from_user.id)


if __name__ == '__main__':
    utils.count_rows()
    random.seed()
    bot.infinity_polling()