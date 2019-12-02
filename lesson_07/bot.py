# -*- coding: utf-8 -*-

import telebot
import re
from telebot import types

token = 'ваш_токен'
bot = telebot.TeleBot(token)

# Регулярное выражение, реагирующее на 2 введённых через пробел числа
digits_pattern = re.compile(r'^[0-9]+ [0-9]+$', re.MULTILINE)

# Иконки, выводимые в качестве превью к результатам
plus_icon = "https://pp.vk.me/c627626/v627626512/2a627/7dlh4RRhd24.jpg"
minus_icon = "https://pp.vk.me/c627626/v627626512/2a635/ILYe7N2n8Zo.jpg"
divide_icon = "https://pp.vk.me/c627626/v627626512/2a620/oAvUk7Awps0.jpg"
multiply_icon = "https://pp.vk.me/c627626/v627626512/2a62e/xqnPMigaP5c.jpg"
error_icon = "https://pp.vk.me/c627626/v627626512/2a67a/ZvTeGq6Mf88.jpg"


# При отсутствии запроса ( = пустой запрос) выводим некоторую информацию
@bot.inline_handler(lambda query: len(query.query) is 0)
def empty_query(query):
    hint = "Введите ровно 2 числа и получите результат!"
    try:
        r = types.InlineQueryResultArticle(
                id='1',
                title="Бот \"Математика\"",
                description=hint,
                # Текст сообщения, которое будет выводиться при нажатии на подсказку
                input_message_content=types.InputTextMessageContent(
                message_text="Эх, зря я не ввёл 2 числа :(")
        )
        bot.answer_inline_query(query.id, [r], cache_time=86400)
    except Exception as e:
        print(e)


@bot.inline_handler(lambda query: len(query.query) > 0)
def query_text(query):
    try:
        matches = re.match(digits_pattern, query.query)
    # Вылавливаем ошибку, если вдруг юзер ввёл чушь
    # или задумался после ввода первого числа
    except AttributeError as ex:
        return
    # В этом месте мы уже уверены, что всё хорошо,
    # поэтому достаем числа
    num1, num2 = matches.group().split()
    try:
        m_sum = int(num1) + int(num2)
        r_sum = types.InlineQueryResultArticle(
                id='1', title="Сумма",
                # Описание отображается в подсказке,
                # message_text - то, что будет отправлено в виде сообщения
                description="Результат: {!s}".format(m_sum),
                input_message_content=types.InputTextMessageContent(
                message_text="{!s} + {!s} = {!s}".format(num1, num2, m_sum)),
                # Указываем ссылку на превью и его размеры
                thumb_url=plus_icon, thumb_width=48, thumb_height=48
        )
        m_sub = int(num1) - int(num2)
        r_sub = types.InlineQueryResultArticle(
                id='2', title="Разность",
                description="Результат: {!s}".format(m_sub),
                input_message_content=types.InputTextMessageContent(
                message_text="{!s} - {!s} = {!s}".format(num1, num2, m_sub)),
                thumb_url=minus_icon, thumb_width=48, thumb_height=48
        )
        # Учтем деление на ноль и подготовим 2 варианта развития событий
        if num2 is not "0":
            m_div = int(num1) / int(num2)
            r_div = types.InlineQueryResultArticle(
                    id='3', title="Частное",
                    description="Результат: {0:.2f}".format(m_div),
                    input_message_content=types.InputTextMessageContent(
                    message_text="{0!s} / {1!s} = {2:.2f}".format(num1, num2, m_div)),
                    thumb_url=divide_icon, thumb_width=48, thumb_height=48
            )
        else:
            r_div = types.InlineQueryResultArticle(
                    id='3', title="Частное", description="На ноль делить нельзя!",
                    input_message_content=types.InputTextMessageContent(
                    message_text="Я нехороший человек и делю на ноль!"),
                    thumb_url=error_icon, thumb_width=48, thumb_height=48,
                    # Сделаем превью кликабельным, по нажатию юзера направят по ссылке
                    url="https://ru.wikipedia.org/wiki/%D0%94%D0%B5%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5_%D0%BD%D0%B0_%D0%BD%D0%BE%D0%BB%D1%8C",
                    disable_web_page_preview=True,
                    # Не будем показывать URL в подсказке
                    hide_url=True
            )
        m_mul = int(num1) * int(num2)
        r_mul = types.InlineQueryResultArticle(
                id='4', title="Произведение",
                description="Результат: {!s}".format(m_mul),
                input_message_content=types.InputTextMessageContent(
                message_text="{!s} * {!s} = {!s}".format(num1, num2, m_mul)),
                thumb_url=multiply_icon, thumb_width=48, thumb_height=48
        )
        # В нашем случае, результаты вычислений не изменятся даже через долгие годы, НО!
        # если где-то допущена ошибка и cache_time уже выставлен большим, то это уже никак не исправить (наверное)
        # Для справки: 2147483646 секунд - это 68 с копейками лет :)
        bot.answer_inline_query(query.id, [r_sum, r_sub, r_div, r_mul], cache_time=2147483646)
    except Exception as e:
        print("{!s}\n{!s}".format(type(e), str(e)))


if __name__ == '__main__':
    bot.infinity_polling()
