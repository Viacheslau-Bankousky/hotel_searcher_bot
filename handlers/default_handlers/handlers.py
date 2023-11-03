from telebot.apihelper import ApiTelegramException
from telebot.types import Message, CallbackQuery

import database.database_methods as database
import handlers.handlers_before_request.handlers as handlers
from keyboards.reply.menu_button import menu_button
from loader import my_bot
from logger.logger import logger_wraps, logger
from models.calendar import DetailedTelegramCalendar, MyTranslationCalendar
from models.data_class import UserData
from utils.answers.answers_for_states import answers
from utils.answers.callbacks import callbacks


@logger_wraps()
@my_bot.message_handler(commands=['start'])
def send_basic_greeting(message: Message) -> None:
    """Turns on the bot, calls its basic greeting, displays menu button.

    :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    current_user.user_name = message.from_user.first_name
    logger.info(f'{current_user.user_name} joined us')

    my_bot.send_message(message.from_user.id,
                        text='*Приветствую {}. Я Hotels_Searcher_bot *'
                             '* и я могу помочь вам найти  лучшие отели*'
                             '* на Hotels.com. Для того, чтобы просмотреть список*'
                             '* всего того, что я умею нажмите кнопу МЕНЮ*'.format(
                            message.from_user.first_name),
                        reply_markup=menu_button(),
                        parse_mode='Markdown')


@logger_wraps()
@my_bot.message_handler(commands=['help'])
def help_me(message: Message) -> None:
    """Bot's reaction to the command /help. Calls a function that removes the
    previous inline keyboard and displays it again after displaying
    the message of the entered command

    :param message: current message
    :type message: Message object
    :return: None"""

    my_bot.send_message(chat_id=message.chat.id,
                        text='*Я с удовольствием помогу вам,*'
                             '* воспользуйтесь кнопкой меню, или продолжите начатое)*',
                        parse_mode='Markdown')

    handlers.check_condition_for_two_commands(message)


@logger_wraps()
@my_bot.message_handler(commands=['hello-world'])
def say_hello_world(message: Message) -> None:
    """Bot's reaction to the command hello-world ("easter egg"). Calls a function that removes
    the previous inline keyboard and displays it again after displaying
    the message of the entered command

    :param message: current message
    :type message: Message object
    :return: None"""

    my_bot.send_message(chat_id=message.chat.id,
                        text='*Да-да, и мир приветствует вас тоже)*',
                        parse_mode='Markdown')

    handlers.check_condition_for_two_commands(message)


@logger_wraps()
@my_bot.message_handler(commands=['lowprice'])
def command_low_price(message: Message):
    """Displays a list of the cheapest hotels. The previous inline keyboard is
    removed (if available), all dynamic attributes of the user data-class object are updated.
    The current value of the entered command is set in a special attribute
    of the user data-class

     :param message: current message
     :type message: Message object
     :return: None"""

    current_user = UserData.get_user(message.chat.id)

    handlers.delete_previous_message(message)
    current_user.clear_all()
    current_user.current_command = '/lowprice'
    my_bot.send_message(chat_id=message.chat.id,
                        text='*Что ж, поищем отели подешевле)*',
                        parse_mode='Markdown')
    handlers.initial_function(message)


@logger_wraps()
@my_bot.message_handler(commands=['highprice'])
def command_high_price(message: Message):
    """Displays a list of the most expensive hotels. The previous inline keyboard
     is removed (if available), all dynamic attributes of the user data-class object are updated.
    The current value of the entered command is set in a special attribute
    of the user data-class

    :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    handlers.delete_previous_message(message)
    current_user.clear_all()
    current_user.current_command = '/highprice'
    my_bot.send_message(chat_id=message.chat.id,
                        text='*Что ж, поищем отели подороже)*',
                        parse_mode='Markdown')
    handlers.initial_function(message)


@logger_wraps()
@my_bot.message_handler(commands=['bestdeal'])
def command_best_deal(message: Message):
    """Displays a list of the most suitable hotels by price and distance
     from the city center. The previous inline keyboard
     is removed (if available), all dynamic attributes of the user data-class object are updated.
    The current value of the entered command is set in a special attribute
    of the user data-class

    :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    handlers.delete_previous_message(message)
    current_user.clear_all()
    current_user.current_command = '/bestdeal'
    my_bot.send_message(chat_id=message.chat.id,
                        text='*Что ж, поищем самые лучшие отели)*',
                        parse_mode='Markdown')
    handlers.initial_function(message)


@logger_wraps()
@my_bot.message_handler(commands=['history'])
def command_history(message: Message):
    """Displays a list of all commands entered, the date and time of introduction,
    as well as their results. The previous inline keyboard
    is removed (if available).

    # :param message: current message
    # :type message: Message object
    :return: None"""

    handlers.delete_previous_message(message)
    my_bot.send_message(chat_id=message.chat.id,
                        text='*Что ж, просмотрим историю)*',
                        parse_mode='Markdown')
    database.pull_from_database(message)


@logger_wraps()
@my_bot.message_handler(content_types=['text'])
def send_answer(message: Message) -> None:
    """ Depending on the current state of bot, reacts to any message entered by user

    :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)

    if current_user.zero_condition:
        answers.send_greeting(message)
    elif current_user.first_condition:
        answers.send_initial_answer(message)
    elif current_user.second_condition:
        answers.send_middle_answer(message)
    elif current_user.intermediate_condition:
        answers.send_next_middle_answer(message)
    elif current_user.fifth_condition:
        answers.send_last_answer(message)


@logger_wraps()
@my_bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def first_query_handler(call: CallbackQuery) -> None:
    """Handles callback queries when calendar buttons are pressed

    :param call: current message
    :type call: CallbackQuery object
    :return: None"""

    current_user = UserData.get_user(call.message.chat.id)

    try:
        result, key, step = MyTranslationCalendar(locale='ru').process(call.data)
        if not result and key:
            my_bot.edit_message_text(
                f"Выберите {MyTranslationCalendar.my_LSTEP[step]}",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=key
            )
        elif result:
            logger.info(f'{current_user.user_name} entered {result}')
            current_user = UserData.get_user(call.message.chat.id)
            current_user.date_buffer = result
            my_bot.edit_message_text(f"*Вы ввели {result.strftime('%d.%m.%Y')}*",
                                     chat_id=call.message.chat.id,
                                     message_id=call.message.message_id,
                                     parse_mode='Markdown')
            if current_user.date_flag is False:
                handlers.check_in(call.message)
            else:
                handlers.check_out(call.message)
    except ApiTelegramException:
        logger.exception('Ups... something went wrong')


@logger_wraps()
@my_bot.callback_query_handler(func=lambda call: True)
def second_query_handler(call: CallbackQuery) -> None:
    """Handles callback queries pressed inline buttons keyboard (bot's commands,
    buttons with the hotels, offer further viewing of hotels with the same parameters,
    new search, download new photos or completion of the searching after the first display of the found hotels)

    :param call: current message
    :type call: CallbackQuery object
    :return: None"""

    if call.data == '/bestdeal':
        callbacks.best_deal(message=call.message, callback_id=call.id)
    elif call.data == '/lowprice':
        callbacks.low_price(message=call.message, callback_id=call.id)
    elif call.data == '/highprice':
        callbacks.high_price(message=call.message, callback_id=call.id)
    elif call.data == '/history':
        callbacks.history(message=call.message, callback_id=call.id)
    elif call.data == 'ДА':
        callbacks.yes_button(message=call.message, callback_id=call.id,
                             callback_data=call.data)
    elif call.data == 'НЕТ':
        callbacks.no_button(message=call.message, callback_id=call.id,
                            callback_data=call.data)
    elif call.data == 'Загрузить еще отели':
        callbacks.new_hotels(message=call.message, callback_id=call.id,
                             callback_data=call.data)
    elif call.data == 'Новый поиск':
        callbacks.new_search(message=call.message, callback_id=call.id,
                             callback_data=call.data)
    elif call.data == 'Закончить поиск':
        callbacks.end_search(message=call.message, callback_id=call.id,
                             callback_data=call.data)
    else:
        callbacks.show_hotels(message=call.message, callback_id=call.id,
                              callback_data=call.data)
