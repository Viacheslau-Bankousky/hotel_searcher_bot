from datetime import date

import emoji
from telebot.apihelper import ApiTelegramException
from telebot.types import Message

import database.database_methods as database
import handlers.default_handlers.handlers as commands
import keyboards.inline.inline_keyboards as inline
from handlers.handlers_for_request_and_after.rapidapi import request_to_api, result_displaying
from loader import my_bot
from logger.logger import logger_wraps, logger
from models.data_class import UserData


@logger_wraps()
def initial_function(message: Message) -> None:
    """""The initial handler of user's messages, offering
    to select the city in which the hotel will be searched, аdds a user 
    to the database (if he is not there), writes the name of next 
    function in the corresponding field of the user data class, directing
    response to the command input validation handler. 

    :param message: current message
    :type message: Message object
    :return: None"""""

    current_user = UserData.get_user(message.chat.id)
    database.add_user_to_database(message)
    result = my_bot.send_message(chat_id=message.chat.id,
                                 text='*Теперь выберите город, для поиска отеля  *',
                                 parse_mode='Markdown')
    current_user.next_function = determination_city
    my_bot.register_next_step_handler(result, check_message)


@logger_wraps()
def determination_city(message: Message) -> None:
    """The handler that interacts with entered message (the selected city)
    and offers to re-enter if its format specified incorrectly
    (using command input validation handler);
    if the message format is specified correctly it displays the variants
    of found cities

    :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)

    logger.info(f'{message.from_user.first_name} looking for hotels in the city - {message.text}')
    if message.text.isalpha() or [letter for letter in message.text
                                  if letter.isspace() or letter.isalpha()]:
        current_user.city = message.text.lower()
        result_waiting(message)
    else:
        result = my_bot.send_message(chat_id=message.chat.id,
                                     text='*Кажется вы ввели не совсем то, что надо) *'
                                          '*Попробуйте еще раз указать название города *',
                                     parse_mode='Markdown')
        my_bot.register_next_step_handler(result, check_message)


@logger_wraps()
def differance_between_commands(message: Message) -> None:
    """Depending on the initial commands,
    it offers to choose either the desired number of hotels
    (when entering lowprice and highprice commands), or the minimum cost
    per day of stay in it (when entering the best deal command). The name of the
    following function is written in a special field of the user data class.
    The message is sent to the command input verification function.
    The current state of the bot is changed.

    :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)

    current_user.first_condition = False
    current_user.second_condition = True
    if current_user.current_command in ('/lowprice', '/highprice'):
        result = my_bot.send_message(chat_id=message.chat.id,
                                     text='*А сейчас выберите количество отелей*',
                                     parse_mode='Markdown')
        current_user.next_function = hotels_count
        my_bot.register_next_step_handler(result, check_message)
    else:
        result = my_bot.send_message(chat_id=message.chat.id,
                                     text='*Введите минимальную цену*'
                                          '* за сутки в отеле (в долларах)*',
                                     parse_mode='Markdown')
        current_user.next_function = minimum_price
        my_bot.register_next_step_handler(result, check_message)


@logger_wraps()
def minimum_price(message: Message) -> None:
    """The handler that interacts with the entered
    message (the minimum cost of the hotel) and offers to re-enter,
    if its format is specified incorrectly. If the correct message is entered,
    offers to specify the maximum cost per night of staying at the hotel.
    The name of the following function is written in a special field of the user data class.
    The message is sent to the command input verification function.

    :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    logger.info(f'{message.from_user.first_name} has chosen the minimum price - {message.text}')

    if message.text.isdigit():
        if int(message.text) > 0:
            current_user.minimum_price = int(message.text)
            result = my_bot.send_message(chat_id=message.chat.id,
                                         text='*Введите максимальную цену*'
                                              '* за сутки проживания в отеле (в долларах)*',
                                         parse_mode='Markdown')
            current_user.next_function = maximum_price
            my_bot.register_next_step_handler(result, check_message)
        else:
            result = my_bot.send_message(chat_id=message.chat.id,
                                         text='*Вы введи не допустимую сумму.*'
                                              '* Попробуйте еще раз*',
                                         parse_mode='Markdown')
            my_bot.register_next_step_handler(result, check_message)
    else:
        result = my_bot.send_message(chat_id=message.chat.id,
                                     text='*Попробуйте ввести другую сумму*',
                                     parse_mode='Markdown')
        my_bot.register_next_step_handler(result, check_message)


@logger_wraps()
def maximum_price(message: Message) -> None:
    """The handler that interacts with the entered
    a message (the maximum cost of the hotel) and offers to re-enter,
    if its format is specified incorrectly. If the correct message is entered,
    suggests specifying the minimum distance of the hotel from the city center.
    The name of the following function is written in a special field of the data class.
    The message is sent to the command input verification function.

    :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    logger.info(f'{message.from_user.first_name} has chosen the maximum price - {message.text}')

    if message.text.isdigit():
        if 0 < int(message.text) > current_user.minimum_price:
            current_user.maximum_price = int(message.text)
            result = my_bot.send_message(chat_id=message.chat.id,
                                         text='*Введите минимальное расстояние *'
                                              '*от отеля до центра города (в км)*',
                                         parse_mode='Markdown')
            current_user.next_function = minimum_distance
            my_bot.register_next_step_handler(result, check_message)
        else:
            result = my_bot.send_message(chat_id=message.chat.id,
                                         text='*Вы ввели  сумму, которая меньше*'
                                              '* указанной первоначально.*'
                                              '* Попробуйте еще раз*',
                                         parse_mode='Markdown')
            my_bot.register_next_step_handler(result, check_message)
    else:
        result = my_bot.send_message(chat_id=message.chat.id,
                                     text='*Попробуйте ввести другую сумму*',
                                     parse_mode='Markdown')
        my_bot.register_next_step_handler(result, check_message)


@logger_wraps()
def minimum_distance(message: Message) -> None:
    """The handler that interacts with an entered message
    (the minimum distance of the hotel from the city center) and
    offers to re-enter if its format is specified incorrectly.
    If the correct message is entered, it offers to specify
    the maximum distance of the hotel from the city center.
    The name of the following function is written in a special field
    of the data class. Message it is sent to the command input verification function.

    :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    logger.info(f'{message.from_user.first_name} has chosen the minimum distance - {message.text}')

    try:
        if message.text.isdigit():
            if int(message.text) > 0:
                current_user.minimum_distance = int(message.text)
                result = my_bot.send_message(chat_id=message.chat.id,
                                             text='*Введите максимальное расстояние *'
                                                  '* от отеля до центра города (в км)*',
                                             parse_mode='Markdown')
                current_user.next_function = maximum_distance
                my_bot.register_next_step_handler(result, check_message)
            else:
                result = my_bot.send_message(chat_id=message.chat.id,
                                             text='*Вы ввели не допустимое расстояние.*'
                                                  '* Попробуйте еще раз*',
                                             parse_mode='Markdown')
                my_bot.register_next_step_handler(result, check_message)
        else:
            result = my_bot.send_message(chat_id=message.chat.id,
                                         text='*Попробуйте ввести другое расстояние*',
                                         parse_mode='Markdown')
            my_bot.register_next_step_handler(result, check_message)
    except ValueError:
        logger.exception('ups... something went wrong')


@logger_wraps()
def maximum_distance(message: Message) -> None:
    """The handler that interacts with the entered
    a message (the maximum distance from the city center) and
    offers to enter it again if its format is specified incorrectly.
    If the correct message is entered, it offers to specify
    the displayed number of hotels.
    The name of the following function is written in a special field of the data class.
    The message is sent to the command input verification function.

    :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    logger.info(f'{message.from_user.first_name} has chosen the maximum distance - {message.text}')

    if message.text.isdigit():
        if 0 < int(message.text) > current_user.minimum_distance:
            current_user.maximum_distance = int(message.text)
            result = my_bot.send_message(chat_id=message.chat.id,
                                         text='*Теперь выберите количество отелей,*'
                                              '* которое хотите посмотреть *',
                                         parse_mode='Markdown')
            current_user.next_function = hotels_count
            my_bot.register_next_step_handler(result, check_message)
        else:
            result = my_bot.send_message(chat_id=message.chat.id,
                                         text='*Вы ввели  расстояние, которое меньше*'
                                              '* указанного первоначально.*'
                                              '* Попробуйте еще раз*',
                                         parse_mode='Markdown')
            my_bot.register_next_step_handler(result, check_message)
    else:
        result = my_bot.send_message(chat_id=message.chat.id,
                                     text='*Попробуйте ввести другое расстояние*',
                                     parse_mode='Markdown')
        my_bot.register_next_step_handler(result, check_message)


@logger_wraps()
def hotels_count(message: Message) -> None:
    """The handler that interacts with the entered
    message (the number of hotels) and offers to re-enter,
    if its format is specified incorrectly. If the message format is correct,
    it is suggested to indicate the number of adults who are going to check
    into the hotel. The name of the following function is written in a special field
    of the user data class. The message is sent to the command input verification function.

    :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    logger.info(f'{message.from_user.first_name} has chosen to view {message.text} hotels')

    if message.text.isdigit():
        if 0 < int(message.text) < 6:
            current_user.hotels_count = int(message.text)
            my_bot.send_message(chat_id=message.chat.id,
                                text='*Хорошо, я запомню)*',
                                parse_mode='Markdown')
            result = my_bot.send_message(chat_id=message.chat.id,
                                         text='*Какое количество взрослых планируют*'
                                              '* проживать в отеле?*',
                                         parse_mode='Markdown')
            current_user.next_function = adults_count
            my_bot.register_next_step_handler(result, check_message)
        else:
            result = my_bot.send_message(chat_id=message.chat.id,
                                         text='*Вы ввели не допустимое количество отелей.*'
                                              '* Для удобного отображения на экране лучше *'
                                              '* выберите от 1 до 5 и попробуйте еще раз)*',
                                         parse_mode='Markdown')
            my_bot.register_next_step_handler(result, check_message)
    else:
        result = my_bot.send_message(chat_id=message.chat.id,
                                     text='*Кажется вы ввели не совсем то, что надо) *'
                                          '* Попробуйте еще раз указать количество отелей*'
                                          '* используя только цифры*',
                                     parse_mode='Markdown')
        my_bot.register_next_step_handler(result, check_message)


@logger_wraps()
def adults_count(message: Message) -> None:
    """The handler that interacts with the entered
    message (the number of adults checking into the hotel) and offers to re-enter,
    if its format is specified incorrectly. If the correct message is entered,
    offers select the check-in date at the hotel. The current state of the bot
    is changing

    :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    logger.info(f'{message.from_user.first_name} has selected {message.text} users to check in')

    if message.text.isdigit():
        if 0 < int(message.text) < 4:
            current_user.adults_count = message.text
            my_bot.send_message(chat_id=message.chat.id,
                                text='*Хорошо я запомню)*'
                                     '* Теперь выберите  дату заселения*',
                                parse_mode='Markdown')
            inline.date_selection(message)
        else:
            result = my_bot.send_message(chat_id=message.chat.id,
                                         text='*Кажется вы ввели слишком много людей) *'
                                              '* Попробуйте еще раз (желательно не более 3)*',
                                         parse_mode='Markdown')
            my_bot.register_next_step_handler(result, check_message)

    else:
        result = my_bot.send_message(chat_id=message.chat.id,
                                     text='*Кажется вы ввели не совсем то, что надо) *'
                                          '* Попробуйте еще раз указать количество*'
                                          '* людей, которые будут заселяться в отель,*'
                                          '* используя только цифры*',
                                     parse_mode='Markdown')
        my_bot.register_next_step_handler(result, check_message)


@logger_wraps()
def check_in(message: Message) -> None:
    """The handler that interacts with the entered
    message (the date of check-in at the hotel) and offers to re-enter,
    if it is specified incorrectly. If the correct message is entered,
    the question is asked about the date on which the accommodation is planned
    in the hotel. The date_flag attribute of the user data class object determines the priority
    of calling the check_in and check_out functions. The entered date is taken
    from a special buffer attribute

    :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)

    if not str(current_user.date_buffer - date.today()).startswith('-'):
        current_user.check_in = current_user.date_buffer
        my_bot.send_message(chat_id=message.chat.id,
                            text='*Выберите дату, до которой планируете *'
                                 '*проживать в отеле*',
                            parse_mode='Markdown')
        current_user.date_flag = True
        inline.date_selection(message)
    else:
        my_bot.send_message(chat_id=message.chat.id,
                            text='*Была указана дата из прошлого.*'
                                 '* Попробуйте еще раз*',
                            parse_mode='Markdown')
        inline.date_selection(message)


@logger_wraps()
def check_out(message: Message) -> None:
    """The handler that interacts with the entered message (the date on which you plan to stay
    at the hotel) and offers to enter it again if it is specified incorrectly. The entered date
    is taken from a special buffer attribute of the user data class. If the correct message
    is entered, the API request function is called. The current state of the bot is changed.

    :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)

    if not str(current_user.date_buffer - date.today()).startswith('-'):
        if not str(current_user.date_buffer - current_user.check_in).startswith('-'):
            current_user.check_out = current_user.date_buffer
            current_user.second_condition = False
            current_user.third_condition = True
            result_waiting(message)
        else:
            my_bot.send_message(chat_id=message.chat.id,
                                text='* Указана не допустимая дата *'
                                     '* (меньше даты заселения). *'
                                     '* Попробуйте еще раз*',
                                parse_mode='Markdown')
            inline.date_selection(message)
    else:
        my_bot.send_message(chat_id=message.chat.id,
                            text='*Была указана дата из прошлого.*'
                                 '* Попробуйте еще раз*',
                            parse_mode='Markdown')
        inline.date_selection(message)


@logger_wraps()
def check_message(message: Message) -> None:
    """Checks whether the entered messages correspond to the main ones
    commands of the bot or causes a response to the pressed
    menu button. Redirection to the corresponding function is carried out with
    a positive result or transition to the next stage of the scenario
    (the next_function attribute of the user class object is used). if the /help and
    /hello-world commands are entered, after calling them, the validator function
    is called again (because these 2 commands do not play a special role in
    the further logic of the bot)

    :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)

    if message.text == '/lowprice':
        commands.command_low_price(message)
    elif message.text == '/highprice':
        commands.command_high_price(message)
    elif message.text == '/bestdeal':
        commands.command_best_deal(message)
    elif message.text == '/history':
        commands.command_history(message)
    elif message.text == '/hello-world':
        commands.say_hello_world(message)
        my_bot.send_message(chat_id=message.chat.id,
                            text='*Теперь можете продолжить с предыдущего шага *'
                                 '* и ввести то, что не успели*', parse_mode='Markdown')
        my_bot.register_next_step_handler(message, check_message)
    elif message.text == '/help':
        commands.help_me(message)
        my_bot.register_next_step_handler(message, check_message)
    elif message.text == emoji.emojize('Меню   :desert_island:'):
        inline.commands_keyboard(message)
    elif message.text == '/start':
        commands.send_basic_greeting(message)
    else:
        current_user.next_function(message)


@logger_wraps()
def yes_answer_about_photo(message: Message) -> None:
    """The handler of command, responding to a positive response, the question
    about displaying photos of the hotel and calling the function of selecting
    quantities of them. Initially the name of the following function is written in a special field
    of the user data class. The message is sent to the command input verification function.
    Emoji message of waiting result is forcibly deleted.

    :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    logger.info(f'{current_user.user_name} will view the photo')

    delete_previous_message(message)
    result = my_bot.send_message(chat_id=message.chat.id,
                                 text='*Какое количество фотографий *'
                                      '* хотите  отобразить на экране? *',
                                 parse_mode='Markdown')
    current_user.intermediate_condition = False
    current_user.fourth_condition = True
    current_user.next_function = photo_count
    my_bot.register_next_step_handler(result, check_message)


@logger_wraps()
def no_answer_about_photo(message: Message) -> None:
    """The handler of the command, responding to a negative response of question
    about displaying the hotel's photos. Emoji message of waiting result  is forcibly
    deleted. The state of the bot changes and the function is called that accesses the API

    :param message: current message
    :type message: Message object
    :return: None"""

    logger.info(f'{message.from_user.first_name} will not view the photo')
    current_user = UserData.get_user(message.chat.id)
    delete_previous_message(message)
    my_bot.send_message(chat_id=message.chat.id,
                        text='*Значит будем без фотографий) *',
                        parse_mode='Markdown')
    current_user.intermediate_condition = False
    current_user.fourth_condition = True
    result_waiting(message)


@logger_wraps()
def photo_count(message: Message) -> None:
    """The handler interacts with an entered message (the number of displayed photos of the hotel)
    and offers to re-enter if its format is specified incorrectly. The  function is called that
    accesses the API

    :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    logger.info(f'{message.from_user.first_name} has selected {message.text} photos to view')

    if message.text.isdigit():
        if 0 < int(message.text) < 11:
            current_user.photo_count = int(message.text)
            my_bot.send_message(chat_id=message.chat.id,
                                text='*Хорошо я запомню)*',
                                parse_mode='Markdown')
            result_waiting(message)
        else:
            result = my_bot.send_message(chat_id=message.chat.id,
                                         text='*Вы ввели не допустимое количество*'
                                              '* фотографий. Для удобного просмотра*'
                                              '* выберите от 1 до 10*',
                                         parse_mode='Markdown')
            my_bot.register_next_step_handler(result, check_message)
    else:
        result = my_bot.send_message(chat_id=message.chat.id,
                                     text='*Кажется вы ввели не совсем то, что надо. *'
                                          '* Попробуйте ввести еще раз необходимое *'
                                          '* количество фото, используя только цифры*',
                                     parse_mode='Markdown')
        my_bot.register_next_step_handler(result, check_message)


@logger_wraps()
def delete_previous_message(message: Message) -> None:
    """Removes the previous built-in buttons or messages if it is possible
    and necessary

    :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    try:
        if current_user.delete_message is True:
            my_bot.delete_message(chat_id=message.chat.id,
                                  message_id=current_user.id_message_for_delete)
            current_user.delete_message = False
    # in case of pressing the menu button too fast repeatedly an exception occurs
    except ApiTelegramException:
        logger.exception('ups... nothing to delete')


@logger_wraps()
def check_condition_for_two_commands(message: Message) -> None:
    """Depending on the current state, it removes either the inline keyboard
    with variants of found cities,  question about viewing photos, the  calendar
    or suggestion to continue or end the searching hotels,
    and then displays them again below the entered message (necessary for
    the /help and /hello-world command is entered in the corresponding state
    of the bot)

    :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    delete_previous_message(message)
    if current_user.first_condition:
        inline.cities_keyboard(message)
    elif current_user.second_condition:
        inline.date_selection(message)
    elif current_user.intermediate_condition:
        inline.yes_no_keyboard(message)
    elif current_user.fifth_condition:
        if current_user.start_from_the_beginning_if_there_is_something_to_show:
            inline.show_more_hotels_if_there_are_available_variants(message)
        elif current_user.start_from_the_beginning_if_nothing_to_show:
            inline.show_more_hotels_if_nothing_to_show(message)


@logger_wraps()
def result_waiting(message: Message):
    """Calls a function that accesses the API to get the required number of hotels.
    Displays a waiting message and gif-image, and after receiving
    a response from the API-function, deletes them (The gif-message id
    is recorded to the special field of user data class, for subsequent
    forced deletion, if something went wrong)

    :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)

    try:
        first_result = my_bot.send_message(chat_id=message.chat.id,
                                           text='*Выполняю поиск. Подождите немного*',
                                           parse_mode='Markdown')

        second_result = my_bot.send_video(message.chat.id,
                                          'https://i.gifer.com/FWcb.gif', None, 'Text')
        current_user.id_message_for_delete = second_result.message_id
        current_user.delete_message = True

        if request_to_api(message):
            if current_user.intermediate_condition:
                inline.yes_no_keyboard(message)
            elif current_user.continue_searching:
                current_user.continue_searching = False
                result_displaying(message)
            my_bot.delete_message(chat_id=message.chat.id,
                                  message_id=second_result.message_id)
            my_bot.delete_message(chat_id=message.chat.id,
                                  message_id=first_result.message_id)
    except (ApiTelegramException, RuntimeError):
        logger.exception('ups... something went wrong')
