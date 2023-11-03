import emoji
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

import handlers.handlers_before_request.handlers as handlers
from loader import my_bot
from logger.logger import logger_wraps
from models.calendar import MyTranslationCalendar
from models.data_class import UserData


@logger_wraps()
def commands_keyboard(message: Message) -> None:
    """Inline keyboard with options for the main most used
    commands (command /help is not displayed because the menu command is available throughout
    the execution of the entire script).The id of the message with the inline keyboard is
    recorded in a special field of the User data class (also the flag field is activated),
    for its further deletion (if necessary). The displayed menu removes the previous inline
    keyboards.

    :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)

    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            text=emoji.emojize('LOWPRICE  :money-mouth_face:'),
            callback_data='/lowprice'),
        InlineKeyboardButton(
            text=emoji.emojize('HIGHPRICE  :zany_face:'),
            callback_data='/highprice'),
        InlineKeyboardButton(
            text=emoji.emojize('BESTDEAL   :partying_face:'),
            callback_data='/bestdeal'),
        InlineKeyboardButton(
            text=emoji.emojize('HISTORY   :brain:'),
            callback_data='/history')
    )
    result = my_bot.send_message(
        chat_id=message.chat.id,
        text='*Для выбора самых дешевых отелей выберите "lowprice"\n\n*'
             '*Для выбора самых дорогих отелей выберите "highprice"\n\n*'
             '*Для выбора отелей, наиболее подходящих по цене\n*'
             '*и расположению от центра горда выберите "bestdeal"\n\n*'
             '*Для отображения истории поиска выберите "history"*',
        reply_markup=keyboard, parse_mode='Markdown'
    )
    handlers.delete_previous_message(message)
    current_user.id_message_for_delete = result.message_id
    current_user.delete_message = True


@logger_wraps()
def yes_no_keyboard(message: Message) -> None:
    """Inline keyboard with answers the question about viewing photos of hotels.
    The id of the message with the inline keyboard is recorded in a special field
    of the User data class (also the flag field is activated), for its further
    deletion (if necessary)

    :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            text=emoji.emojize('ДА   :thumbs_up:'),
            callback_data='ДА'),
        InlineKeyboardButton(
            text=emoji.emojize('НЕТ   :thumbs_down:'),
            callback_data='НЕТ')
    )
    my_bot.send_message(chat_id=message.chat.id,
                        text='*Хотите посмотреть фотографии отелей ?*',
                        parse_mode='Markdown')
    result = my_bot.send_message(chat_id=message.chat.id,
                                 text='*Я с удовольствием вам их покажу)*',
                                 reply_markup=keyboard, parse_mode='Markdown')
    current_user.id_message_for_delete = result.message_id
    current_user.delete_message = True


@logger_wraps()
def date_selection(message: Message) -> None:
    """It creates the calendar for entering the check-in and
    check-out dates from the hotel. ID of the message with the inline
    keyboard is recorded in a special field of the User data class (also the flag field
    is activated), for its further deletion (if necessary)

    :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)

    calendar, step = MyTranslationCalendar(locale='ru').build()
    result = my_bot.send_message(message.chat.id,
                                 f"Введите {MyTranslationCalendar.my_LSTEP[step]}",
                                 reply_markup=calendar)
    current_user.id_message_for_delete = result.message_id
    current_user.delete_message = True


@logger_wraps()
def cities_keyboard(message: Message) -> None:
    """Keyboard with found  cities. The id of the message with the inline keyboard is recorded
    in a special field of the User data class (also the flags field is activated): 1 - for its
    further deletion (if necessary) 2 - for going  to the next function after selecting the city.
    The current state of the bot is changed.

    :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)

    keyboard = InlineKeyboardMarkup()
    for i_element in current_user.current_buffer:
        for key, value in i_element.items():
            keyboard.add(InlineKeyboardButton(text=key, callback_data=value))

    result = my_bot.send_message(chat_id=message.chat.id,
                                 text='*Вот, что я нашел)*', reply_markup=keyboard,
                                 parse_mode='Markdown')
    current_user.id_message_for_delete = result.message_id
    current_user.delete_message = True
    current_user.zero_condition = False
    current_user.first_condition = True


@logger_wraps()
def visit_the_website(message: Message) -> InlineKeyboardMarkup:
    """Creates the keyboard with a single button that opens the hotel's website

    :param message: current message
    :type message: Message object
    :return: inline keyboard
    :rtype: InlineKeyboardMarkup"""

    current_user = UserData.get_user(message.chat.id)
    button = InlineKeyboardButton(
        text='Сайт отеля',
        url=f'https://hotels.com/h{current_user.hotel_id}.Hotel-information'
    )
    keyboard = InlineKeyboardMarkup().add(button)
    return keyboard


@logger_wraps()
def show_more_hotels_if_there_are_available_variants(message: Message) -> None:
    """After the first displaying of the specified number of hotels, it offers to load
    more hotels with the same parameters, start a new searching or stop it.
    The id of the inline keyboard is recorded for later deletion. The current state
    of the bot is changed.

     :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            text=emoji.emojize('Еще отели   :grinning_face_with_big_eyes:'),
            callback_data='Загрузить еще отели'),
        InlineKeyboardButton(
            text=emoji.emojize('Новый поиск   :star-struck:'),
            callback_data='Новый поиск'),
        InlineKeyboardButton(
            text=emoji.emojize('Закончить   :face_with_spiral_eyes:'),
            callback_data='Закончить поиск')
    )
    my_bot.send_message(chat_id=message.chat.id,
                        text='*Хотите продолжить просмотр отелей *'
                             '* с теми же параметрами? *',
                        parse_mode='Markdown')
    result = my_bot.send_message(chat_id=message.chat.id,
                                 text='*Я с удовольствием вам их покажу)*',
                                 reply_markup=keyboard, parse_mode='Markdown')
    current_user.id_message_for_delete = result.message_id
    current_user.delete_message = True
    current_user.fourth_condition = False
    current_user.continue_searching = False
    current_user.fifth_condition = True
    current_user.start_from_the_beginning_if_there_is_something_to_show = True


@logger_wraps()
def show_more_hotels_if_nothing_to_show(message: Message) -> None:
    """Suggests starting a new search or ending the search when there
    are no more hotels by the specified parameter. The id of the inline keyboard
    is recorded for later deletion. The current state of the bot is changed

    :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            text=emoji.emojize('Новый поиск   :star-struck:'),
            callback_data='Новый поиск'),
        InlineKeyboardButton(
            text=emoji.emojize('Закончить поиск   :face_with_spiral_eyes:'),
            callback_data='Закончить поиск')
    )
    my_bot.send_message(chat_id=message.chat.id,
                        text='*Больше по по вашему запросу ничего не найдено.*'
                             '* Хотите поискать новые отели?*',
                        parse_mode='Markdown')
    result = my_bot.send_message(chat_id=message.chat.id,
                                 text='*Я с удовольствием вам их покажу)*',
                                 reply_markup=keyboard, parse_mode='Markdown')
    current_user.id_message_for_delete = result.message_id
    current_user.delete_message = True
    current_user.start_from_the_beginning_if_there_is_something_to_show = False
    current_user.start_from_the_beginning_if_nothing_to_show = True
