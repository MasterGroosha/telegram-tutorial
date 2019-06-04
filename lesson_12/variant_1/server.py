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