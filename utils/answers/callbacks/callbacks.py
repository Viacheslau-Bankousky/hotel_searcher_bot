from telebot.types import Message

import handlers.default_handlers.handlers as commands
import handlers.handlers_before_request.handlers as handlers
import keyboards.inline.inline_keyboards as inline_keyboard
from handlers.handlers_for_request_and_after.rapidapi import delete_showed_hotels
from loader import my_bot
from logger.logger import logger_wraps, logger
from models.data_class import UserData


@logger_wraps()
def best_deal(message: Message, callback_id: int) -> None:
    """Answering the callback after pressing the /bestdeal button

    :param message: current message
    :type message: Message object
    :param callback_id: id of the callback of pressed button
    :type callback_id: integer
    :return: None"""

    my_bot.answer_callback_query(callback_query_id=callback_id)
    commands.command_best_deal(message)


@logger_wraps()
def low_price(message: Message, callback_id: int) -> None:
    """Answering the callback after pressing the /lowprice button

    :param message: current message
    :type message: Message object
    :param callback_id: id of the callback of pressed button
    :type callback_id: integer
    :return: None"""

    my_bot.answer_callback_query(callback_query_id=callback_id)
    commands.command_low_price(message)


@logger_wraps()
def high_price(message: Message, callback_id: int) -> None:
    """Answering the callback after pressing the /highprice button

    :param message: current message
    :type message: Message object
    :param callback_id: id of the callback of pressed button
    :type callback_id: integer
    :return: None"""

    my_bot.answer_callback_query(callback_query_id=callback_id)
    commands.command_high_price(message)


@logger_wraps()
def history(message: Message, callback_id: int) -> None:
    """Answering the callback after pressing the /history button

    :param message: current message
    :type message: Message object
    :param callback_id: id of the callback of pressed button
    :type callback_id: integer
    :return: None"""

    my_bot.answer_callback_query(callback_query_id=callback_id)
    commands.command_history(message)


@logger_wraps()
def yes_button(message: Message, callback_id: int,
               callback_data: str) -> None:
    """Answering the callback after pressing 'yes' button (question about viewing photos),
    displays the data of the pressed button, writes them to the corresponding field of the user
    data class

    :param message: current message
    :type message: Message object
    :param callback_data: data of pressed button
    :type: callback_data: string
    :param callback_id: id of the callback of pressed button
    :type callback_id: integer
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    my_bot.answer_callback_query(callback_query_id=callback_id)
    my_bot.send_message(chat_id=message.chat.id, text=callback_data)
    current_user.answer_about_photo = callback_data
    handlers.yes_answer_about_photo(message)


@logger_wraps()
def no_button(message: Message, callback_id: int,
              callback_data: str) -> None:
    """Answering the callback after pressing the 'no' button (question about viewing a photo),
    displays the data of the pressed button, writes them to the corresponding field of the user
    data class

    :param message: current message
    :type message: Message object
    :param callback_data: data of pressed button
    :type: callback_data: string
    :param callback_id: id of the callback of pressed button
    :type callback_id: integer
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    my_bot.answer_callback_query(callback_query_id=callback_id)
    my_bot.send_message(chat_id=message.chat.id, text=callback_data)
    current_user.answer_about_photo = callback_data
    handlers.no_answer_about_photo(message)


@logger_wraps()
def new_hotels(message: Message, callback_id: int,
               callback_data: str) -> None:
    """Answering the callback after pressing the 'new hotels' button, after the first
     display of the specified number of hotels, displays the data of the pressed
     button, deletes the previous inline keyboard and calling the corresponding
    function that removes the shown hotels

    :param message: current message
    :type message: Message object
    :param callback_data: data of pressed button
    :type: callback_data: string
    :param callback_id: id of the callback of pressed button
    :type callback_id: integer
    :return: None"""

    my_bot.answer_callback_query(callback_query_id=callback_id)
    my_bot.send_message(chat_id=message.chat.id, text=callback_data)
    handlers.delete_previous_message(message)
    delete_showed_hotels(message)


@logger_wraps()
def new_search(message: Message, callback_id: int,
               callback_data: str) -> None:
    """Answering the callback after pressing the 'new search' button, after the first
    display of the specified number of hotels, displays the data of the pressed
    button and calling list of available commands

    :param message: current message
    :type message: Message object
    :param callback_data: data of pressed button
    :type: callback_data: string
    :param callback_id: id of the callback of pressed button
    :type callback_id: integer
    :return: None"""

    my_bot.answer_callback_query(callback_query_id=callback_id)
    my_bot.send_message(chat_id=message.chat.id, text=callback_data)
    inline_keyboard.commands_keyboard(message)


@logger_wraps()
def end_search(message: Message, callback_id: int,
               callback_data: str) -> None:
    """Answering the callback after pressing the 'end search' button, after the first
    displaying of the specified number of hotels, displays the data of the pressed
    button, deletes the previous inline keyboard  and sends farewell message.
    At the end, all dynamic attributes of the user data class are returned to the
    default (initial) value

    :param message: current message
    :type message: Message object
    :param callback_data: data of pressed button
    :type: callback_data: string
    :param callback_id: id of the callback of pressed button
    :type callback_id: integer
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    my_bot.answer_callback_query(callback_query_id=callback_id)
    my_bot.send_message(chat_id=message.chat.id, text=callback_data)
    handlers.delete_previous_message(message)
    my_bot.send_message(chat_id=message.chat.id,
                        text='*Спасибо, что выбрали меня. Обращайтесь снова*'
                             '* при любой необходимости)*',
                        parse_mode='Markdown')
    current_user.clear_all()


@logger_wraps()
def show_hotels(message: Message, callback_id: int,
                callback_data: str) -> None:
    """Answering the callback after pressing the button with selected city from the cities list,
    displays the data of the pressed button, writes the destination id to the corresponding
    dynamic attribute of the user data class, deletes the previous inline keyboard

    :param message: current message
    :type message: Message object
    :param callback_data: data of pressed button
    :type: callback_data: string
    :param callback_id: id of the callback of pressed button
    :type callback_id: integer
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    for i_element in current_user.current_buffer:
        for key, value in i_element.items():
            if callback_data == value:
                my_bot.answer_callback_query(callback_query_id=callback_id)
                my_bot.send_message(chat_id=message.chat.id,
                                    text=f'Хорошо, я запомню ваш выбор: {key}')
                logger.info(f'{current_user.user_name} has selected {key}')
                current_user.destination_id = value
                handlers.delete_previous_message(message)
                handlers.differance_between_commands(message)
            break
