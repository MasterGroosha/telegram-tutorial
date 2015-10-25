# -*- coding: utf-8 -*-

import shelve
from telebot import types
from random import shuffle
from lesson_02.SQLighter import SQLighter
from lesson_02.config import database_name, shelve_name


def count_rows():
    """
    Данный метод считает общее количество строк в базе данных и сохраняет в хранилище.
    Потом из этого количества будем выбирать музыку.
    """
    db = SQLighter(database_name)
    rowsnum = db.count_rows()
    storage = shelve.open(shelve_name)
    storage['rows_count'] = rowsnum
    storage.close()


def get_rows_count():
    """
    Получает из хранилища количество строк в БД
    :return: (int) Число строк
    """
    storage = shelve.open(shelve_name)
    rowsnum = storage['rows_count']
    storage.close()
    return rowsnum


def set_user_game(chat_id, estimated_answer):
    """
    Записываем юзера в игроки и запоминаем, что он должен ответить.
    :param chat_id: id юзера
    :param estimated_answer: правильный ответ (из БД)
    """
    storage = shelve.open(shelve_name)
    storage[str(chat_id)] = estimated_answer
    storage.close()


def finish_user_game(chat_id):
    """
    Заканчиваем игру текущего пользователя и удаляем правильный ответ из хранилища
    :param chat_id: id юзера
    """
    storage = shelve.open(shelve_name)
    del storage[str(chat_id)]
    storage.close()


def get_answer_for_user(chat_id):
    """
    Получаем правильный ответ для текущего юзера.
    В случае, если человек просто ввёл какие-то символы, не начав игру, возвращаем None
    :param chat_id: id юзера
    :return: (str) Правильный ответ / None
    """
    storage = shelve.open(shelve_name)
    try:
        answer = storage[str(chat_id)]
        return answer
    # Если человек не играет, ничего не возвращаем
    except KeyError:
        return None


def generate_markup(right_answer, wrong_answers):
    """
    Создаем кастомную клавиатуру для выбора ответа
    :param right_answer: Правильный ответ
    :param wrong_answers: Набор неправильных ответов
    :return: Объект кастомной клавиатуры
    """
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    # Склеиваем правильный ответ с неправильными
    all_answers = '{},{}'.format(right_answer, wrong_answers)
    # Создаем лист (массив) и записываем в него все элементы
    list_items = []
    for item in all_answers.split(','):
        list_items.append(item)
    # Хорошенько перемешаем все элементы
    shuffle(list_items)
    # Заполняем разметку перемешанными элементами
    for item in list_items:
        markup.add(item)
    return markup
