import os
import time

import logging
import requests
import telegram

from dotenv import load_dotenv
from requests.exceptions import HTTPError

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = "https://praktikum.yandex.ru/api/user_api/homework_statuses/"
HEADERS = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
bot_client = telegram.Bot(token=TELEGRAM_TOKEN)

STATUS_ERROR = 'Получен не ожидаемый статус работы: {status}'
BOT_ERROR = 'Бот столкнулся с ошибкой: {e}'
REQUEST_ERROR = ('Ошибка запроса по адресу: {url}, параметры: {params}, '
                 '{headers}. Текст ошибки: {e}')
BAD_STATUS = ('Попытка обращения к серверу: {url} имеет ошибку {error}. '
              'Параметры: {params}')
CODE_ERROR = ('Попытка обращения к серверу: {url}, параметры: {params}.'
              'В результате присутствует {code}. Ошибка {error}.')
STATUSES = {
    'approved': 'Ревьюеру всё понравилось, можно приступать к следующему '
                'уроку.',
    'rejected': 'К сожалению в работе нашлись ошибки.',
}
ANSWER = 'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def parse_homework_status(homework):
    status = homework['status']
    result = STATUSES.get(status)
    if not result:
        raise ValueError(STATUS_ERROR.format(status=status))
    homework_name = homework['homework_name']
    return ANSWER.format(homework_name=homework_name, verdict=result)


def get_homework_statuses(current_timestamp):
    params = {
        'from_date': current_timestamp,
    }
    try:
        response = requests.get(URL,
                                headers=HEADERS,
                                params=params)
    except requests.exceptions.HTTPError as e:
        raise requests.exceptions.HTTPError(REQUEST_ERROR.format(
            url=URL,
            params=params,
            headers=HEADERS,
            e=e,
        ))
    resp = response.json()
    if 'error' in resp:
        error = resp['error']['error']
        raise ValueError(BAD_STATUS.format(
            error=error,
            url=URL,
            params=params
        ))
    elif 'code' in resp:
        code = resp.get('code', 'Unknown code')
        error = resp['message']
        raise ValueError(CODE_ERROR.format(
            code=code,
            error=error,
            url=URL,
            params=params
        ))
    return resp


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID,
                                   text=message)


def main():
    current_timestamp = int(time.time())
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]), bot_client)

            current_timestamp = new_homework.get('current_date',
                                                 current_timestamp)
            time.sleep(600)
        except Exception as e:
            logging.error(BOT_ERROR.format(e=e))


if __name__ == '__main__':
    logging.basicConfig(
        filename=__file__ + '.log',
        format='%(asctime)s %(funcName)s %(message)s'
    )
    main()
