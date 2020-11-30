import os
import time

import requests
import telegram

from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(
    filename='logs.log',
    format='%(asctime)s %(funcName)s %(message)s'
)
PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = "https://praktikum.yandex.ru/api/user_api/homework_statuses/"
HEADERS = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
BOT_CLIENT = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    status = homework['status']
    homework_name = homework['homework_name']
    if status == 'rejected':
        verdict = (
            'К сожалению в работе нашлись ошибки.'
        )
    elif status == 'approved':
        verdict = (
            'Ревьюеру всё понравилось, можно приступать к следующему '
            'уроку.'
        )
    else:
        verdict = (
            f'Получен статус: {status}. Ошибка'
        )
        return logging.warning(
            f'Получен не ожидаемый статус работы: {status}'
        )
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    params = {
        'from_date': current_timestamp,
    }
    try:
        response = requests.get(URL,
                                headers=HEADERS,
                                params=params)
        return response.json()
    except (ConnectionError, TimeoutError, ValueError) as ex:
        return logging.error(
                f'Error at {ex}, request on server praktikum'
        )


def send_message(message, bot_client):
    return BOT_CLIENT.send_message(chat_id=CHAT_ID,
                                   text=message)


def main():
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
            time.sleep(5)
            return logging.error(f'Бот столкнулся с ошибкой: {e}')


if __name__ == '__main__':
    main()
