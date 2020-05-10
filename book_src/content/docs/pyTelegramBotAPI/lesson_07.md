---
title: "Урок 7"
description: "Встраиваемые боты (Inline)"
type: docs
url: "/docs/lesson_07"
BookToC: true
weight: 8
---

## ⚠️ Важно!
Код, приведённый здесь, актуален для первой версии Bot API. Пожалуйста, откройте [урок 8]({{< relref "/docs/pytelegrambotapi/lesson_08" >}}), чтобы узнать о важных изменениях.

## Введение

4 января 2016 года разработчики Telegram выпустили большое дополнение к существующему BotAPI, заключающееся в появлении [встраиваемых ботов](https://telegram.org/blog/inline-bots).  
К сожалению, не все до конца понимают, в чем их особенность. А вот в чем: если раньше для того, чтобы получить какую-либо информацию от бота и перекинуть её собеседнику нужно было открывать диалог с ботом, писать всякие команды, а потом пересылать ответ в нужный чат, то теперь всё стало быстрее и проще (для некоторых ситуаций): просто открываете нужный чат, вызываете бота, введя его ник в поле ввода сообщения, ставите пробел и пишете свой запрос. Бот отвечает на эти запросы в виде всплывающих подсказок, число и содержание которых зависит от того, что вы написали боту и от заложенного в него алгоритма. Если одна из подсказок удовлетворяет вашему запросу, нажимаете на неё и некоторое сообщение отправляется в тот чат, в котором вы находитесь.  
Например, если вы хотите отправить своему собеседнику ссылку на статью о Telegram из русскоязычной Википедии, то достаточно ввести в поле ввода @wiki ru Telegram и подождать пару секунд. Результат представлен на рисунке:

{{% img2 src="/images/l7_1.jpg" caption="Рис. 1. Как выглядят результаты запросов от встраиваемых ботов" %}}

Соответственно, если вы нажмете на одну из этих подсказок, то ссылка на соответствующую статью будет отправлена в текущий чат. Собственно, всё!  
Помимо ссылок, при помощи Inline API можно отправлять фотографии, GIF-анимации, видеоанимации в формате Mpeg-4 и ссылки на видеозаписи, которые можно будет смотреть прямо в приложении.

Прежде, чем мы начнём писать своего встраиваемого бота, несколько слов о том, для чего **НЕ** надо их использовать и какие есть ограничения. Во-первых, такие боты нужны именно для подсказок, когда вы хотите чем-то поделиться, но вам нужна помощь бота. Вы же не помните все ссылки на те самые видео с котиками? А бот быстренько поможет его найти, чтобы вы поделились им в чатике. Во-вторых, существуют недокументированные ограничения по объемам отправляемой информации. Скажем, для текстов и ссылок нельзя отправлять элементы длиннее 300-400 символов (на самом деле, получается без проблем около двухсот, больше - с оговорками). На мой взгляд, это самый неприятный момент в API. Я давеча пытался прикрутить поиск цитат с сайта [Bash.im](https://bash.im) из своей базы для одного из моих [ботов](https://t.me/bashim_bot). Увы, всё, чего удалось добиться, это отправка коротких цитат (примерно с твит размером) непосредственно текстом, длинных - через отправку ссылок на сам Баш.

## Простой инлайн-бот

Ну а теперь приступим к созданию нашего первого встраиваемого бота. Вообще говоря, никто не мешает добавить существующему Inline-возможности, но дабы не усложнять код, напишем отдельного.  
Что же он будет уметь? Пусть на вход боту будут подаваться 2 числа, а он в подсказках будет предлагать основные математические действия: сложение, вычитание, умножение и деление. Да, пример надуманный, но как нельзя лучше показывает особенности Inline API.
В начале, зарегистрируем бота у [@BotFather](https://t.me/botfather) (или воспользуемся имеющимся) для него вызовем команду /setinline.  
**Внимание**: после ввода этой команды и выбора бота нужно ввести подсказку, появляющуюся в поле ввода при вызове нашего бота в дальнейшем, иначе фокус не удастся.
  
Создадим файл исходного кода и добавим туда необходимые импорты и объект самого бота:

```python
# -*- coding: utf-8 -*-

import telebot
import re
from telebot import types

token = 'ваш_токен'
bot = telebot.TeleBot(token)
```

Мы условились, что на вход будут подаваться 2 числа, поэтому нам нужно построить регулярное выражение, которое будет реагировать на корректный ввод. Оно очень простое:  
`digits_pattern = re.compile(r'^[0-9]+ [0-9]+$', re.MULTILINE)`

А теперь самое главное - логика. Пока юзер пишет, Телеграм никак себя не проявляет, но как только он делает паузу, приложение считает, что это законченный ввод и отправляет его боту. Юзер дописал ещё пару символов и остановился? Окей, снова кидаем это боту. Соответственно, может сложиться ситуация, когда пользователь ввёл одно число и задумался. Наш парсер, попробовав сопоставить текст на наличие регулярного выражение, ругнётся и сотворит всякие нехорошие вещи, например, остановит весь скрипт (мы же помним, что Python - интерпретируемый язык, да?). Значит, надо ставить ловлю исключений:

```python
try:
    matches = re.match(digits_pattern, query.query)
except AttributeError as ex:
    return
```

Если условие выше отработало без ошибок, значит, мы получили два искомых числа. Теперь начинаются особенности Inline API. Каждая подсказка, присылаемая ботом, это объект с набором некоторых характеристик. Мы будем использовать объект типа "Статья".
Согласно [документации](https://core.telegram.org/bots/api#inline-mode), обязательных параметров у такого объекта четыре: тип, уникальный идентификатор, заголовок и объект, который будет отправлен, чаще всего текст. По поводу типа можно не беспокоиться: используемая мной уже больше полугода библиотека [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI) подставит нужное значение сама. Уникальный идентификатор придется ставить самим и тут есть подвох: при использовании подгрузки (об этом в конце урока) идентификаторы должны быть уникальными у всех значений в одном большом запросе (т.е. у исходных результатов и всех подгружаемых в пределах одного запроса). Учтите это. Заголовок - очевидно. Отправляемый текст - то, что будет отправлено в текущий чат при нажатии на данную подсказку.  
Есть ещё необязательный параметр "описание" (description). Так вот, описание != отправляемый текст. В подсказке может быть написано "Наполеон - это торт", а в отправляемом тексте могут содержаться коды запуска ядерный ракет. Шутка, но смысл понятен.

Вооружившись этими знаниями и имея на руках два присланных пользователем числа, давайте создадим 4 объекта, каждый из которых отвечает за свою математическую операцию (на самом деле 5, т.к. учтем деление на ноль):

```python
num1, num2 = matches.group().split()
try:
    m_sum = int(num1) + int(num2)
    r_sum = types.InlineQueryResultArticle(
            id='1', title="Сумма",
            # Описание отображается в подсказке,
            # message_text - то, что будет отправлено в виде сообщения
            description="Результат: {!s}".format(m_sum),
            input_message_content=types.InputTextMessageContent(
            message_text="{!s} + {!s} = {!s}".format(num1, num2, m_sum))
    )
    m_sub = int(num1) - int(num2)
    r_sub = types.InlineQueryResultArticle(
            id='2', title="Разность",
            description="Результат: {!s}".format(m_sub),
            input_message_content=types.InputTextMessageContent(
            message_text="{!s} - {!s} = {!s}".format(num1, num2, m_sub))
    )
    # Учтем деление на ноль и подготовим 2 варианта развития событий
    if num2 is not "0":
        m_div = int(num1) / int(num2)
        r_div = types.InlineQueryResultArticle(
                id='3', title="Частное",
                description="Результат: {0:.2f}".format(m_div),
                input_message_content=types.InputTextMessageContent(
                message_text="{0!s} / {1!s} = {2:.2f}".format(num1, num2, m_div))
        )
    else:
        r_div = types.InlineQueryResultArticle(
                id='3', title="Частное", description="На ноль делить нельзя!",
                input_message_content=types.InputTextMessageContent(
                message_text="Я нехороший человек и делю на ноль!")
        )
    m_mul = int(num1) * int(num2)
    r_mul = types.InlineQueryResultArticle(
            id='4', title="Произведение",
            description="Результат: {!s}".format(m_mul),
            input_message_content=types.InputTextMessageContent(
            message_text="{!s} * {!s} = {!s}".format(num1, num2, m_mul))
    )
    bot.answer_inline_query(query.id, [r_sum, r_sub, r_div, r_mul])
except Exception as e:
    print("{!s}\n{!s}".format(type(e), str(e)))
```

Полагаю, тут ничего сверхсложного нет. Вызывает интерес только последняя строка, а именно метод `answer_inline_query`. У него обязательных параметров два: уникальный идентификатор запроса (его получает хэндлер, так что про него забываем) и массив ответов. Загоняем теперь предыдущие два куска кода в одну функцию, обернутую хэндлером:

```python
@bot.inline_handler(func=lambda query: len(query.query) > 0)
def query_text(query):
    (тут два куска кода, приведённых выше)
```

И можно запускать! Введём в любом чате, кроме секретного, ник нашего бота и два числа. Смотрим на подсказку:

{{% img2 src="/images/l7_2.jpg" caption="Рис. 2. Результат работы бота" %}}

## Дизайн и подсказки

В принципе, правильно, но как-то не наглядно. Да и не очень понятно для нового пользователя, как, что и зачем.  
А давайте учтем ситуацию, когда пользователь ввёл только ник бота, и покажем ему подсказку:

```python
@bot.inline_handler(func=lambda query: len(query.query) is 0)
def empty_query(query):
    hint = "Введите ровно 2 числа и получите результат!"
    try:
        r = types.InlineQueryResultArticle(
                id='1',
                parse_mode='Markdown',
                title="Бот \"Математика\"",
                description=hint,
                input_message_content=types.InputTextMessageContent(
                message_text="Эх, зря я не ввёл 2 числа :(")
        )
        bot.answer_inline_query(query.id, [r])
    except Exception as e:
        print(e)
```

Уже лучше, но всё равно не очень наглядно. А давайте добавим превью для каждой подсказки, чтобы слева была иконка соответствующей операции, и, заодно, сделаем превью при делении на ноль кликабельным, отправляя пользователя на [эту страницу Википедии](https://ru.wikipedia.org/wiki/Деление_на_ноль).  
Во-первых, закачаем на какой-нибудь бесплатный хостинг иконки с нашими математическими операциями (сгенерировал в [Metro Studio](https://www.syncfusion.com/downloads/metrostudio), размер каждой 48х48 px):

```python
plus_icon = "https://pp.vk.me/c627626/v627626512/2a627/7dlh4RRhd24.jpg"
minus_icon = "https://pp.vk.me/c627626/v627626512/2a635/ILYe7N2n8Zo.jpg"
divide_icon = "https://pp.vk.me/c627626/v627626512/2a620/oAvUk7Awps0.jpg"
multiply_icon = "https://pp.vk.me/c627626/v627626512/2a62e/xqnPMigaP5c.jpg"
error_icon = "https://pp.vk.me/c627626/v627626512/2a67a/ZvTeGq6Mf88.jpg"
```

Во-вторых, отредактируем функцию `query_text`, добавив к каждому объекту типа "Статья" иконку, а для деления на ноль - свою иконку и ссылку:

```python
@bot.inline_handler(func=lambda query: len(query.query) > 0)
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
```

Обратите снова внимание на функцию `answer_inline_query`, в ней я добавил аргумент `cache_time`. Значит он именно то, что первым приходит в голову — устанавливает время, на которое результат будет закэширован, чтобы лишний раз не дергать бота. Сейчас на моей стороне тот факт, что математика - фундаментальная наука, и за те 68 с копейками лет, что указаны у меня в аргументе `cache_time`, результат операций не изменится. Но! Выше на рис. 2 у меня слева от подсказок нет ничего, никаких картинок. И да, в течение 68 с лишним лет конкретно для данного запроса так и будет. Поэтому трижды подумайте, прежде чем установите большое время кэширования. Для каких-то динамических результатов, например, для подсказки при нулевом запросе, вполне достаточно времени 86400 (1 сутки). По умолчанию, кстати, вообще всего 300 секунд, т.е. 5 минут.

Теперь наши результаты выглядят куда симпатичнее:

{{< columns >}} <!-- begin columns block -->
{{% img2 src="/images/l7_3.jpg" %}}
<---> <!-- magic sparator, between columns -->
{{% img2 src="/images/l7_4.jpg" %}}
{{< /columns >}}

Прекрасно! Мы написали своего первого встраиваемого бота! Но...
Но есть ещё такая штука, как `offset`. Вообще говоря, это нужно для постепенной подгрузки новых результатов. Например, пользователь запрашивает видео с котиками, бот возвращает пять штук. Как только юзер долистывает до конца, бот запрашивает у своего источника ещё пять, а Telegram дописывает их к уже имеющимся. В итоге, уже 10 вариантов и так далее. В одном из своих ботов я сделал так: запрашиваю из БД 5 записей с `offset` равным нулю. При отправке их пользователю, я устанавливаю в функции `answer_inline_query` параметр `next_offset` в значение 5 (строковый параметр, если что). Если юзер долистал до конца, то боту придет запрос с этим же текстом, но с значением `offset` как раз 5, поэтому в следующий раз я из БД запрошу уже следующие пять записей, прибавлю ещё пятерку к текущему значению, получая 10 и снова верну пользователю значения. Как только у меня закончились соответствующие запросу данные в базе, отправляю пустую строку в качестве аргумента `next_offset`. В общем, всё выглядит примерно так (бОльшая часть кода вырезана для упрощения понимания):

```python
def query_text(query):
    offset = int(query.offset) if query.offset else 0
    with sqlite3.connect('quotes.db') as connection:
        cursor = connection.cursor()
        # Тут используется SQLite Full-Text Search, не пугайтесь
        quotes = cursor.execute("SELECT num, text FROM quotes WHERE quotes.id IN (SELECT rowid FROM fts WHERE text MATCH ?) LIMIT 5 OFFSET ?", (query.query, offset,)).fetchall()
    if len(quotes) is 0:
        try:
            result = types.InlineQueryResultArticle(id='1',
                                           title=(заголовок),
                                           description=(описание),
                                           input_message_content=types.InputTextMessageContent(
                                           message_text="(текст)"))
            bot.answer_inline_query(query.id, [result])
        except Exception as e:
            print(e)
        return
    results_array = []
    try:
        m_next_offset = str(offset + 5) if len(quotes) == 5 else None
        for index, quote in enumerate(quotes):
            try:
                # При использовании подгрузки, ID должны быть уникальными в пределах всей большой пачки!
                results_array.append(types.InlineQueryResultArticle(id=str(offset + index),
                                           title=(заголовок),
                                           description=(описание),
                                           input_message_content=types.InputTextMessageContent(
                                           message_text=(текст)),
                                           )
                                    )
            except Exception as e:
                print(e)
        # устанавливаем новый offset или сбрасываем, если в БД закончились релевантные записи
        bot.answer_inline_query(query.id, results_array, next_offset=m_next_offset if m_next_offset else "")
    except Exception as e:
        print(e)
```

На этом урок действительно закончен.

{{< btn_left relref="/docs/pytelegrambotapi/lesson_06" >}}Урок №6{{< /btn_left >}}
{{< btn_right relref="/docs/pytelegrambotapi/lesson_08" >}}Урок №8{{< /btn_right >}}
