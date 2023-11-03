from telebot.types import BotCommand

from config import DEFAULT_COMMANDS
from logger.logger import logger_wraps


@logger_wraps()
def set_default_commands(my_bot) -> None:
    """Sets default commands of the bot

    :param: my_bot: current Telegram bot
    :type: my_bot: TeleBot object
    :return: None"""

    my_bot.set_my_commands(
        [BotCommand(*command) for command in DEFAULT_COMMANDS]
    )
