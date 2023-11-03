import datetime
from collections import OrderedDict
from typing import Dict, List, Tuple, Union, Callable

import emoji
import requests
from requests.models import Response
from telebot.apihelper import ApiTelegramException
from telebot.types import Message, InputMediaPhoto

import config
import database.database_methods as database
import handlers.handlers_before_request.handlers as handlers
import keyboards.inline.inline_keyboards as inline
from loader import my_bot
from logger.logger import logger_wraps, logger
from models.data_class import UserData


@logger_wraps()
def locations(message: Message) -> Tuple[Dict[str, str],
Dict[str, str], str]:
    """Gets the endpoint url, querystring and headers for getting possible hotels locations
     and returns them

    :param: message: current message
    :type: message: Message object
    :return: headers, querystring, url
    :rtype: Tuple[Dict[str, str], Dict[str, str], str]"""

    current_user = UserData.get_user(message.chat.id)
    url = "https://hotels4.p.rapidapi.com/locations/v3/search"
    querystring = {
        "q": f"{current_user.city}", "locale": "ru_RU"
    }

    headers = {
        "X-RapidAPI-Key": config.RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    return headers, querystring, url


@logger_wraps()
def properties(message: Message) -> Tuple[Dict[str, str], Dict[str,
Union[str, int, datetime.date]], str]:
    """Gets the endpoint url, payload and headers for getting main properties of the selected hotel
    and returns them

    :param: message: current message
    :type: message: Message object
    :return: headers, payload, url
    :rtype: Tuple[Dict[str, str], Dict[str, Union[str, int, datetime.date]], str]"""

    current_user = UserData.get_user(message.chat.id)
    in_day, in_month, in_year = map(int, current_user.check_in.strftime('%y-%m-%d').split('-'))
    out_day, out_month, out_year = map(int, current_user.check_out.strftime('%y-%m-%d').split('-'))
    command: str = current_user.current_command
    url = "https://hotels4.p.rapidapi.com/properties/v2/list"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "ru_RU",
        "destination": {"regionId": current_user.destination_id},
        "checkInDate": {
            "day": in_day,
            "month": in_month,
            "year": in_year
        },
        "checkOutDate": {
            "day": out_day,
            "month": out_month,
            "year": out_year
        },
        "rooms": [
            {
                "adults": int(current_user.adults_count)
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": 200,
        "sort": "PRICE_LOW_TO_HIGH",
    }

    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": config.RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    return headers, payload, url


@logger_wraps()
def detailed_description(message: Message) -> Tuple[Dict[str, str],
Dict[str, Union[str, int]], str]:
    """Gets the endpoint url, payload and headers for getting detailed desctiption
    of the selected hotel and returns them

    :param: message: current message
    :type: message: Message object
    :return: headers, querystring, url
    :rtype: Tuple[Dict[str, str], Dict[str, Union[str, int]], str]"""

    current_user = UserData.get_user(message.chat.id)

    url = "https://hotels4.p.rapidapi.com/properties/v2/get-summary"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "ru_RU",
        "propertyId": current_user.hotel_id
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": config.RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    return headers, payload, url


@logger_wraps()
def function_selection(message: Message) -> Callable:
    """Depending on the current state of the bot, it calls the corresponding
    function that returns the url, headers, query string/payload

    :param message: argument
    :type message: Message object
    :return: function for getting data for request (headers, querystring/payload, url)
    :rtype: Callable"""

    current_user = UserData.get_user(message.chat.id)

    if current_user.zero_condition:
        return locations(message)
    elif current_user.third_condition:
        return properties(message)
    elif current_user.fourth_condition:
        return detailed_description(message)


@logger_wraps()
def request_helper(message: Message) -> requests.Response:
    """Depending on the current state of the bot, gets headers, querustring/payload, url and sends
     a request to the corresponding API endpoint

    :param: message: current message
    :type: message: Message object
    :return: response from API endpoin
    :rtype: Response object"""

    current_user = UserData.get_user(message.chat.id)
    if current_user.zero_condition:
        headers, querystring, url = function_selection(message)
        response = requests.get(url, headers=headers,
                                params=querystring, timeout=10)

        return response
    elif current_user.third_condition:
        headers, payload, url = function_selection(message)
        response = requests.post(url, json=payload, headers=headers)

        return response
    elif current_user.fourth_condition:
        headers, payload, url = function_selection(message)
        response = requests.post(url, json=payload, headers=headers)

        return response


@logger_wraps()
def create_request(message: Message) -> requests.Response:
    """Executes a request to the corresponding API endpoint using an auxiliary function.
    If something went wrong, repeats the request the specified number of times

    :param: message: current message
    :type: message: Message object
    :return: response from  the corresponding API endpoint or informs the user about an unsuccessful
    attempt to obtain data
    :rtype: Response object"""

    current_user = UserData.get_user(message.chat.id)

    try:
        current_user.connect_attempt += 1
        response: Response = request_helper(message)
        if response.status_code == requests.codes.ok:

            return response

        else:
            my_bot.send_message(chat_id=message.chat.id,
                                text='*Упс, кажется что-то пошло не так.*'
                                     '* Сейчас попробую еще раз*',
                                parse_mode='Markdown')
            if current_user.connect_attempt < 3:
                request_to_api(message)
            else:
                my_bot.send_message(chat_id=message.chat.id,
                                    text='*Сейчас я не могу помочь вам.*'
                                         '* Попробуйте еще раз немного позже*',
                                    parse_mode='Markdown')
                handlers.delete_previous_message(message)
    except requests.exceptions.Timeout:
        my_bot.send_message(chat_id=message.chat.id,
                            text='*Кажется появились какие-то проблемы*'
                                 '* с соединением. Сейчас попробую еще раз*',
                            parse_mode='Markdown')
        request_to_api(message)


@logger_wraps()
def request_to_api(message: Message) -> bool:
    """Depending on the current state of the bot, it calls the corresponding functions
    for processing incoming data. At the same time, if necessary, executes a request
    to the corresponding API endpoint using an auxiliary function

    :param: message: current message
    :type: message: Message object
    :return: True in any cases"""

    current_user = UserData.get_user(message.chat.id)
    try:
        if current_user.fourth_condition:
            gets_detailed_hotels_data(message=message)
        else:
            response: Response = create_request(message)

            if current_user.zero_condition:
                gets_possible_hotels(response=response, user=current_user, message=message)
            elif current_user.third_condition:
                gets_main_hotels_data(response=response, user=current_user, message=message)

    except (AttributeError, TypeError):
        logger.exception('ups... something went wrong')

    return True


@logger_wraps()
def processing_cities(message: Message) -> None:
    """Extracts the raw data from the corresponding attribute of the user data class,
    generates a list with hotel locations and re-assigns it to the same attribute.

    :param: message: current message
    :type: message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    all_cities: List[Union[Dict]] = current_user.current_buffer
    current_user.current_buffer = None
    processed_cities = list()
    for i_element in all_cities:
        if "regionNames" in i_element and "essId" in i_element:
            processed_cities.append({i_element.get("regionNames").get(
                "fullName"): i_element.get("essId").get("sourceId")})
    current_user.current_buffer = processed_cities
    inline.cities_keyboard(message)


@logger_wraps()
def gets_possible_hotels(response: Response, user: UserData, message: Message) -> None:
    """Assigns the raw data of possible hotel locations to the corresponding attribute of the user
    data class or informs that nothing have been found for the specified parameters

    :param: message: current message
    :type: message: Message object
    :param: response: response from the corresponding API endpoint
    :type: response: Response
    :param: user: current user
    :type: user: UserData
    :return: None"""

    suggestions: List[Union[Dict]] = response.json().get("sr")
    if len(suggestions) != 0:
        user.current_buffer: List[Union[Dict]] = suggestions
        processing_cities(message)
    else:
        result = my_bot.send_message(chat_id=message.chat.id,
                                     text='*По вашему запросу ничего не найдено.*'
                                          '* Попробуйте выбрать другие варианты*',
                                     parse_mode='Markdown')
        my_bot.register_next_step_handler(result, handlers.determination_city)


@logger_wraps()
def gets_main_hotels_data(response: Response, user: UserData, message: Message) -> None:
    """Gets main information about each hotel from raw data and adds it to a special dynamic
    attribute of the user data class. Changes the current state of the bot

    :param: message: current message
    :type: message: Message object
    :param: response: response from the corresponding API endpoint
    :type: response: Response
    :param: user: current user
    :type: user: UserData
    :return: None"""

    user.current_buffer = OrderedDict()
    hotels_data: List[Dict] = response.json().get("data", "").get("propertySearch", "").get("properties")

    for item in hotels_data:
        hotel_id: str = item.get("id")
        user.current_buffer[hotel_id] = {
            "name": item.get("name", ""),
            "price": item.get("price", "").get("lead", "").get("amount", ""),
            "remoteness": item.get("destinationInfo", "").get("distanceFromDestination", "").get("value", 0)
        }
    check_entered_commands(message)
    user.third_condition = False
    user.intermediate_condition = True


@logger_wraps()
def gets_detailed_hotels_data(message: Message) -> None:
    """Gets additional information about each hotel from the corresponding API endpoint and adds it
    to a special dynamic attribute of the user data class

    :param: message: current message
    :type: message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    hotels_ids = list(current_user.current_buffer.keys())
    hotels_count: int = current_user.hotels_count
    buffer: OrderedDict[str, Dict] = current_user.current_buffer
    for item in hotels_ids[:hotels_count]:
        current_hotel: Dict[str, Union[str, int]] = buffer.get(item, "")
        current_user.hotel_id = item
        response: Response = create_request(message)
        response_data = response.json().get("data").get("propertyInfo", "")
        current_hotel["address"] = response_data.get("summary", "").get("location", "").get(
            "address", "").get("addressLine", "")
        current_hotel["rating"] = response_data.get("summary", "").get("overview", "").get(
            "propertyRating", "").get("rating", "")
        current_hotel["images"] = []

        for item in response_data.get("propertyGallery", "").get("images", ""):
            current_hotel["images"].append(item.get("image", "").get("url"))
    result_displaying(message)


@logger_wraps()
def check_entered_commands(message: Message) -> None:
    """Depending on the entered command, calls the appropriate function to sort the data
    (when using the /lowprice command, the data comes from the API in the form already
    sorted in ascending order of price)

    :param: message: current message
    :type: message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    if current_user.current_command == '/bestdeal':
        best_deal(message)
    elif current_user.current_command == '/highprice':
        high_price(message)


@logger_wraps()
def high_price(message: Message) -> None:
    """Sort hotels by descending prices and adds them to a special dynamic attribute
    of the user data class

    :param: message: current message
    :type: message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    sorted_by_price_hotels: List[Tuple[str, Dict[Any]]] = sorted(
        current_user.current_buffer.items(),
        key=lambda x: x[1].get("price"),
        reverse=True
    )
    current_user.current_buffer = OrderedDict(sorted_by_price_hotels)


@logger_wraps()
def best_deal(message: Message) -> None:
    """Sort hotels in a given range of prices and distances to the city center and adds them
     to a special dynamic attribute of the user data class

    :param: message: current message
    :type: message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    hotels: OrderedDict[str, Dict[Any]] = current_user.current_buffer
    hotels_sorted_by_price_and_remoteness: List[Tuple[str, Dict[Any]]] = sorted(
        hotels.items(),
        key=lambda x: (current_user.maximum_distance >= x[1].get("remoteness") >= current_user.minimum_distance,
                       current_user.maximum_price >= x[1].get("price") >= current_user.minimum_price)
    )
    current_user.current_buffer = OrderedDict(hotels_sorted_by_price_and_remoteness)


@logger_wraps()
def result_displaying(message: Message) -> None:
    """Depending on the current number of hotels, displays them with or without photos.
    After displaying, an inline keyboard is displayed, offering to continue the
    search with the same parameters (if possible), start a new search or stop it

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    hotels: OrderedDict[str, Dict[Any]] = current_user.current_buffer
    if len(hotels.keys()) >= current_user.hotels_count:
        for index in range(current_user.hotels_count):
            check_photo_answer(message, index=index)
        inline.show_more_hotels_if_there_are_available_variants(message)
    else:
        for index in range(len(hotels.keys())):
            check_photo_answer(message, hotels=hotels, index=index)
        my_bot.send_message(chat_id=message.chat.id,
                            text='*К сожалению мне удалось найти немного*'
                                 '* меньше отелей(*',
                            parse_mode='Markdown')
        inline.show_more_hotels_if_nothing_to_show(message)


@logger_wraps()
def check_photo_answer(message: Message, index: int) -> None:
    """Checks whether it is necessary to display photos of hotels and, depending on the user's answer,
    calls the appropriate functions that send information about them

    :param message: argument
    :type message: Message object
    :param: index: index of current hotel in list
    :type: index: integer
    :param: hotels:
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    current_user.current_hotel_index = index
    if current_user.answer_about_photo == 'ДА':
        gets_need_count_of_hotel_urls(message)
    else:
        my_bot.send_message(chat_id=message.chat.id,
                            text=create_text_message(message),
                            reply_markup=inline.visit_the_website(message),
                            parse_mode='Markdown')


@logger_wraps()
def gets_need_count_of_hotel_urls(message: Message) -> None:
    """Gets the required number of url photos of the hotel. If the quantity does not match
    the one set by the user, it will show all available

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    all_hotels: OrderedDict[str, Dict[Any]] = current_user.current_buffer
    hotels_ids = list(all_hotels.keys())
    current_hotel_index: int = current_user.current_hotel_index
    current_hotel_id: str = hotels_ids[current_hotel_index]
    hotel_photos: List[str] = all_hotels.get(current_hotel_id).get("images")
    try:
        if len(hotel_photos) < current_user.photo_count:
            raise ValueError
        create_media_group(message, hotel_photos[: current_user.photo_count])
    except ValueError:
        my_bot.send_message(chat_id=message.chat.id,
                            text='*У следующего отеля будет  меньше фото,*'
                                 '* чем вы хотели*', parse_mode='Markdown')
        create_media_group(message, hotel_photos[: len(hotel_photos)])


@logger_wraps()
def create_media_group(message: Message, photo: List[Union[str]]) -> None:
    """Creates a media group to send messages with photos

    :param message: argument
    :type message: Message object
    :param: photo: url of hotel photos
    :type: photo: List with strings
    :return: None"""

    try:
        my_bot.send_media_group(message.chat.id,
                                [InputMediaPhoto(url,
                                                 caption=create_text_message(message))
                                 if photo.index(url) == 0
                                 else InputMediaPhoto(url)
                                 for url in photo])
        my_bot.send_message(chat_id=message.chat.id,
                            text=emoji.emojize(
                                '*Для просмотра дополнительных опций и фотографий *'
                                '* посетите  :backhand_index_pointing_down:*'),
                            reply_markup=inline.visit_the_website(message),
                            parse_mode='Markdown')
    except ApiTelegramException:
        logger.exception('ups... something went wrong')


@logger_wraps()
def create_text_message(message: Message) -> str:
    """Creates and returns the text message with a description of each hotel

    :param message: current message
    :type message: Message object
    :return: description of the hotel
    :rtype: string"""

    current_user = UserData.get_user(message.chat.id)
    hotels: OrderedDict[str, Dict[Any]] = current_user.current_buffer
    index: int = current_user.current_hotel_index
    hotel_item: Dict[Any] = hotels.get(list(hotels.keys())[index])
    try:
        # This design is used to determine the total length of stay at the hotel
        date_diff: List[int] = [
            int(m) for m in str(current_user.check_out - current_user.check_in)
            if m.isdigit()
        ]
        if date_diff[0] == 0:
            date_diff[0] = 1

        current_message = emoji.emojize(
            ':hotel: Название отеля: '
            f'{hotel_item.get("name", "")}\n'
            ':magnifying_glass_tilted_right: Адрес: '
            f'{hotel_item.get("address", ":house_with_garden:")}\n'
            ':bar_chart: Общий рейтинг отеля: '
            f'{hotel_item.get("rating", ":smiling_face:")}\n'
            f':pinching_hand: Расстояние от центра города: '
            f'{hotel_item.get("remoteness")}\n'
            ':coin: Цена за сутки: '
            f'{round(hotel_item.get("price") / date_diff[0], 2)} USD\n'
            f':money_bag: Цена за {date_diff[0]} дней проживания: '
            f'{hotel_item.get("price")}'
            f' USD\n'
        )
        database.add_results_to_database(message, result=current_message)
        return current_message
    except TypeError:
        logger.exception('oops... something went wrong')


@logger_wraps()
def delete_showed_hotels(message: Message) -> None:
    """Deletes the number of hotels entered by the user from current_buffer (attribute
    of the user data class), after they are displayed. Changes the current state of the bot.
    With the help of an auxiliary function, it accesses the API and receives new data from there.
    If there are no more hotels in the list, the keyboard is displayed, offering to start the
    search with new parameters or stop it

    :param message: current message
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    hotels: OrderedDict[str, Dict[Any]] = current_user.current_buffer
    hotels_ids = list(hotels.keys())
    try:
        for index in range(current_user.hotels_count):
            hotel_for_delete: str = hotels_ids[index]
            hotels.pop(hotel_for_delete)
        current_user.fifth_condition = False
        current_user.start_from_the_beginning_if_there_is_something_to_show = False
        current_user.continue_searching = True
        current_user.fourth_condition = True
        handlers.result_waiting(message)
    except IndexError:
        logger.exception('ups... nothing to delete more')
        inline.show_more_hotels_if_nothing_to_show(message)
