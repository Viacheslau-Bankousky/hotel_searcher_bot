from peewee import InternalError
from requests.exceptions import ConnectionError
from telebot.apihelper import ApiTelegramException
from urllib3.exceptions import ReadTimeoutError

from database.database_methods import create_database
from loader import my_bot
from logger.logger import logger
from utils.set_bot_commands import set_default_commands

from handlers.default_handlers import *


if __name__ == '__main__':
    try:
        set_default_commands(my_bot)
        create_database()
        my_bot.infinity_polling(timeout=0)
    except (ConnectionError, ReadTimeoutError, InternalError,
            ApiTelegramException):
        logger.exception('ups... something went wrong')