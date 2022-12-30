import json
import logging

import requests

import config
from config import TelegramConfig


class Telegram:

    __bot_token = ""
    __bot_chatID = ""

    def __init__(self, localconfig: TelegramConfig):
        self.__bot_token = localconfig.token
        self.__bot_chatID = localconfig.chat_id

    def send(self, message):
        send_text = 'https://api.telegram.org/bot' + self.__bot_token + \
                    '/sendMessage?chat_id=' + self.__bot_chatID + '&text=' + message

        response = requests.get(send_text)

        if not response.json()['ok']:
            logging.warning(json.dumps(response.json(), indent=4))
        return response.json()

    def send_photo(self, filename):

        image = open(filename, 'rb')

        send_text = 'https://api.telegram.org/bot' + self.__bot_token + \
                    '/sendPhoto?chat_id=' + self.__bot_chatID

        response = requests.post(send_text, files={'photo': image})

        if not response.json()['ok']:
            logging.warning(json.dumps(response.json(), indent=4))
        return response
