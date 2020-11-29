import os
import time

import requests
import telegram

from dotenv import load_dotenv
import logging

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = "https://praktikum.yandex.ru/api/user_api/homework_statuses/"
headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}


def parse_homework_status(homework):
    params = {
        'from_date': 0,
    }
    homework_name = homework['homework_name']
    if homework['status'] == 'rejected':
        verdict = \
            'К сожалению в работе нашлись ошибки.'
    else:
        verdict = \
            'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    params = {
        'from_date': current_timestamp,
    }
    homework_statuses = requests.get(
        url=URL,
        headers=headers,
        params=params,
    )
    while True:
        try:
            homework_statuses = requests.get(URL, headers=headers,
                                             params=params)
            return homework_statuses.json()
        except Exception as ex:
            time.sleep(600)
            return logging.error("Error at %s", "request on server praktikum",
                                 exc_info=ex)


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID,
                                   text=message)


def main():
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())  # начальное значение timestamp
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get('current_date',
                                                 current_timestamp)
            time.sleep(600)  # опрашивать раз в 10 минут

        except Exception as e:
            print(f'Бот столкнулся с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
