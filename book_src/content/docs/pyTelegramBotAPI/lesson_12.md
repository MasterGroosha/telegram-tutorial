---
title: "Урок 12"
description: "Запускаем несколько ботов на одном сервере"
type: docs
url: "/docs/lesson_12"
BookToC: true
weight: 13
---

## Введение

{{< hint info >}}
Если вы по какой-то причине всё ещё используете **pyTelegramBotAPI**, то этот урок вам сильно пригодится.  
Те, кто уже перешёл на что-то другое (например, **aiogram**) могут продолжать использовать поллинг (polling), а на вебхуки переходить только при увеличении количества пользователей и, следовательно, нагрузки.  
{{< /hint >}}

По моему мнению (а оно может не совпадать с вашим), боты на вебхуках надёжнее ботов, использующих поллинг.  
Связано это в первую очередь с моими воспоминаниями из августа-сентября 2015 года, когда каждую ночь падали боты из-за Gateway Timeout'ов. Затем в Bot API добавили поддержку самоподписанных сертификатов и я начал использовать их, благо это бесплатно.  
В [уроке номер четыре]({{< relref "/docs/pytelegrambotapi/lesson_04" >}}) я писал, что т.к. портов для использования вебхуков всего 4, то, казалось бы, можно на одной машине запустить всего четырёх ботов, и что есть решение этой проблемы. Вот об этом сейчас и пойдет речь. Я планирую разбить материал на две части: в первой мы научимся запускать сколько угодно ботов при помощи одних лишь серверов [CherryPy](http://www.cherrypy.org) и самоподписанных сертификатов, во второй же вместо основного веб-сервера поставим [nginx](http://nginx.org/ru), а вместо самоподписанных сертификатов – бесплатные от [Let's Encrypt](https://letsencrypt.org).

## Вариант первый: CherryPy и самоподписанные сертификаты

Общая схема взаимодействия Telegram и наших ботов в первом варианте будет выглядеть следующим образом: 

{{% img2 src="/images/l12_1.jpg" caption="Общая схема взаимодействия" %}}

### Подготавливаем «роутер»

Давайте для начала создадим наш "роутер", то есть, сервер CherryPy, который будет принимать все сообщения и раскидывать их по нужным ботам. Условимся также, что наш сервер будет иметь IP 122.122.122.122 и вебхуки от первого бота будут приходить на адрес https://122.122.122.122/AAAA, а от второго на https://122.122.122.122/ZZZZ. Предполагается, что вы уже прочитали [урок №4]({{< relref "/docs/pytelegrambotapi/lesson_04" >}}) и структура вебхук-ботов вас не пугает.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cherrypy
import requests
import telebot

WEBHOOK_HOST = 'Здесь.Ваш.IP.Адрес'
WEBHOOK_PORT = 443  # 443, 80, 88 или 8443 
WEBHOOK_LISTEN = '0.0.0.0' # Слушаем отовсюду
WEBHOOK_SSL_CERT = 'webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = 'webhook_pkey.pem'  # Путь к закрытому ключу
WEBHOOK_URL_BASE = "https://{!s}:{!s}".format(WEBHOOK_HOST, WEBHOOK_PORT)

BOT_1_TOKEN = "Токен первого бота"
BOT_2_TOKEN = "Токен второго бота"

# Вводим здесь IP-адреса и порты, куда перенаправлять входящие запросы.
# Т.к. всё на одной машине, то используем локалхост + какие-нибудь свободные порты.
# https в данном случае не нужен, шифровать незачем.
BOT_1_ADDRESS = "http://127.0.0.1:7771"
BOT_2_ADDRESS = "http://127.0.0.1:7772"

bot_1 = telebot.TeleBot(BOT_1_TOKEN)
bot_2 = telebot.TeleBot(BOT_2_TOKEN)

# Описываем наш сервер
class WebhookServer(object):

    # Первый бот (название функции = последняя часть URL вебхука)
    @cherrypy.expose
    def AAAA(self):
        if 'content-length' in cherrypy.request.headers and \
           'content-type' in cherrypy.request.headers and \
           cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            # Вот эта строчка и пересылает все входящие сообщения на нужного бота
            requests.post(BOT_1_ADDRESS, data=json_string)
            return ''
        else:
            raise cherrypy.HTTPError(403)

    # Второй бот (действуем аналогично)
    @cherrypy.expose
    def ZZZZ(self):
        if 'content-length' in cherrypy.request.headers and \
           'content-type' in cherrypy.request.headers and \
           cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            requests.post(BOT_2_ADDRESS, data=json_string)
            return ''
        else:
            raise cherrypy.HTTPError(403)

if __name__ == '__main__':

    bot_1.remove_webhook()
    bot_1.set_webhook(url='https://122.122.122.122/AAAA',
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))    

    bot_2.remove_webhook()
    bot_2.set_webhook(url='https://122.122.122.122/ZZZZ',
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))

    cherrypy.config.update({
        'server.socket_host': WEBHOOK_LISTEN,
        'server.socket_port': WEBHOOK_PORT,
        'server.ssl_module': 'builtin',
        'server.ssl_certificate': WEBHOOK_SSL_CERT,
        'server.ssl_private_key': WEBHOOK_SSL_PRIV,
        'engine.autoreload.on': False
    })
    cherrypy.quickstart(WebhookServer(), '/', {'/': {}})
```

### Подготавливаем ботов

Создадим их две штуки, каждый из которых будет на команду **/start** представляться по своему номеру.  
Первый бот:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cherrypy
import telebot

BOT_TOKEN = "токен нашего бота"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=["start"])
def command_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот номер 1")

class WebhookServer(object):
    # index равнозначно /, т.к. отсутствию части после ip-адреса (грубо говоря)
    @cherrypy.expose
    def index(self):
        length = int(cherrypy.request.headers['content-length'])
        json_string = cherrypy.request.body.read(length).decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''

if __name__ == '__main__':
    cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 7771,
        'engine.autoreload.on': False
    })
    cherrypy.quickstart(WebhookServer(), '/', {'/': {}})
```

Второй делается аналогично, только ставим порт 7772 и меняем сообщение по команде **/start**.
Запускаем "роутер", запускаем ботов. Если мы всё сделали правильно, то при создании чата с первым ботом, сначала вебхук получит "роутер", перешлет его первому серверу, который отправит сообщение непосредственно в Telegram, в точности так же, как на схеме выше.

## Вариант второй: nginx и Let's Encrypt

Этот подход мне лично кажется более правильным и современным. Веб-сервер nginx используется крупнейшими мировыми веб-сайтами, а Let's Encrypt предлагает бесплатные и доверенные сертификаты.

Общая схема взаимодействия Telegram и наших ботов во втором варианте будет выглядеть следующим образом: 

{{% img2 src="/images/l12_2.jpg" caption="Общая схема взаимодействия" %}}

### Получаем сертификат от Let's Encrypt

Используйте официальную утилиту [certbot](https://certbot.eff.org) для получения сертификата. Укажите свою почту и доменное имя вашего сервера (просто IP-адрес не подойдет). Обратите внимание на дату окончания действия сертификата! Каждые 90 дней его надо обновлять (данный процесс легко автоматизируется).

### Настраиваем nginx

Скачиваем и устанавливаем веб-сервер nginx любым удобным для вас способом и открываем `nginx.conf` в каталоге `/etc/nginx`. Внутри блока `http {}` создаем блок `server{}` и заполняем его следующим образом (все основные параметры совпадают с аналогичными из первого варианта):

```
server {
        listen 443 ssl;
        server_name (адрес вашего сервера);

        ssl_protocols       TLSv1 TLSv1.1 TLSv1.2;
        ssl_certificate /etc/letsencrypt/live/(адрес вашего сервера)/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/(адрес вашего сервера)/privkey.pem;


        # Первый бот
        location /AAAA/ {
            proxy_pass         http://127.0.0.1:7771/;
            proxy_redirect     off;
            proxy_set_header   Host $host;
            proxy_set_header   X-Real-IP $remote_addr;
            proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Host $server_name;
        }

        # Второй бот
        location /ZZZZ/ {
            proxy_pass         http://127.0.0.1:7772/;
            proxy_redirect     off;
            proxy_set_header   Host $host;
            proxy_set_header   X-Real-IP $remote_addr;
            proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Host $server_name;
        }
    }
```

Обратите внимание на слэши после номера порта (7771/ и 7772/), их наличие очень важно. Далее сохраняем файл конфигурации и перезапускаем службу: `sudo service nginx reload`.
Единственное, что надо изменить в самих ботах - это добавить `bot.remove_webhook()` и `bot.set_webhook("https://(адрес вашего сервера)/хххх)`, где xxxx в нашем случае либо AAAA, либо ZZZZ, при этом параметр `certificate` в методе `set_webhook` уже не нужен, т.к. сертификат не самоподписанный.

{{< btn_left relref="/docs/pytelegrambotapi/lesson_11" >}}Урок №11{{< /btn_left >}}
{{< btn_right relref="/docs/aiogram/lesson_13" >}}Урок №13{{< /btn_right >}}