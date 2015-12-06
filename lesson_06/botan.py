# -*- coding: utf-8 -*-
# Modified for pyTelegramBotAPI (https://github.com/eternnoir/pyTelegramBotAPI/)

import requests
import json

URL_TEMPLATE = 'https://api.botan.io/track?token={token}&uid={uid}&name={name}'


# Если не нужно собирать ничего, кроме количества использований,
# уберите эту функцию
def make_json(message):
    data = {}
    data['message_id'] = message.message_id
    data['from'] = {}
    data['from']['id'] = message.from_user.id
    if message.from_user.username is not None:
        data['from']['username'] = message.from_user.username
    data['chat'] = {}
    # Chat.Id используется в обоих типах чатов
    data['chat']['id'] = message.chat.id
    return data


def track(token, uid, msg, name='Message'):
    global url_template
    url = URL_TEMPLATE.format(token=str(token), uid=str(uid), name=name)
    headers = {'Content-type': 'application/json'}
    try:
        # Если убрали функцию выше, замените json.dumps(make_json(msg)) на json.dumps({})
        r = requests.post(url, data=json.dumps(make_json(msg)), headers=headers)
        return r.json()
    except requests.exceptions.Timeout:
        return False
    except requests.exceptions.RequestException as e:
        print(e)
        return False