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
HEADERS = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
bot_client = telegram.Bot(token=TELEGRAM_TOKEN)

STATUS_ERROR = 'Получен не ожидаемый статус работы: {status}'
STATUSES = {
    'approved': 'Ревьюеру всё понравилось, можно приступать к следующему '
                'уроку.',
    'rejected': 'К сожалению в работе нашлись ошибки.',
    'else': 'Получен статус: {status}. Ошибка'
}
ANSWER = 'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def parse_homework_status(homework):
    status = homework['status']
    homework_name = homework['homework_name']
    verdikt = ANSWER.format(homework_name=homework_name, verdict=STATUSES[
        status])
    correct = STATUSES.get(status)
    if not correct:
        raise Exception(STATUS_ERROR.format(status=status))
    return verdikt


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
        logging.error(
            f'Error at {ex}, request on server praktikum'
        )


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID,
                                   text=message)


def main():
    current_timestamp = int(time.time())  # начальное значение timestamp
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]), bot_client)
            elif new_homework.get('error'):
                code = new_homework.get('code', 'Unknown code')
                error = new_homework['error']['error']
                logging.exception(f'Попытка обращения к серверу имеет ошибку'
                                  f'{code}. {error}.')
            elif new_homework.get('message'):
                code = new_homework.get('code', 'Unknown code')
                message = new_homework['message']
                logging.exception(f'Попытка обращения к серверу имеет ошибку'
                                  f'{code}. {message}.')
            current_timestamp = new_homework.get('current_date',
                                                 current_timestamp)
            time.sleep(600)  # опрашивать раз в 10 минут

        except Exception as e:
            logging.error(f'Бот столкнулся с ошибкой: {e}')


if __name__ == '__main__':
    logging.basicConfig(
        filename=__file__ + '.log',
        format='%(asctime)s %(funcName)s %(message)s'
    )
    main()
