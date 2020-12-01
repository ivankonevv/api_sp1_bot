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

UNKNOWN_STATUS = 'Получен не ожидаемый статус работы: {status}'
ST = {
    'approved': 'Ревьюеру всё понравилось, можно приступать к следующему '
                'уроку.',
    'rejected': 'К сожалению в работе нашлись ошибки.',
    'else': 'Получен статус: {status}. Ошибка'
}
FINALLY = 'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def parse_homework_status(homework):
    status = homework['status']
    homework_name = homework['homework_name']
    raise NameError(UNKNOWN_STATUS.format(status=status))
    #return FINALLY.format(homework_name=homework_name, verdict=ST[status])


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
                    new_homework.get('homeworks')[0]))
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
