from datetime import date
from typing import List, Dict, Optional, OrderedDict


class UserData:
    """Class for recording temporary data during execution
    script and quick access to it

    :param: user_name: user's first name, which has set by him earlier 
    :type: user_name: string
    :param: current_command: the command, that the user entered
    :type: current_command: string
    :param: city:  the city selected by the user
    :type: city:  string
    :param: hotels_count:  the number of hotels entered by the user
    :type: hotels_count: integer
    :param: hotel_id: id of the selected hotel 
    :type: hotel_id: string
    :param: current_hotel_index: the index of each hotel in the list (in the process
    of sequential display them by the bot)
    :type: current_hotel_index: integer
    :param: destination_id: destination id number  of the selected city
    :type: destination_id: string
    :param: answer_about_foto:  will photos be displayed in the future ? (yes/no) 
    :type: answer_about_foto: string
    :param: photo_count: the count of photos entered by the user 
    :type: foto_count: integer
    :param: adults_count: The number of adults checking into the hotel 
    :type: adults_count: string
    :param: check_in:  check-in date at the hotel 
    :type: check_in:  date object
    :param: check_out:  check-out date from the hotel
    :type: check_out:  date object
    :param: minimum_price:  minimum price per night at the hotel 
    :type: minimum_price: integer
    :param: maximum_price:a  maximum price per night at the hotel
    :type: maximum_price: integer
    :param: minimum_distance: minimum hotel distance from the city center (in km) 
    :type: minimum_distance: integer
    :param: maximum_distance: maximum hotel distance from the city center (in km)
    :type: maximum_distance: integer
    :param: date_buffer: attribute for temporary recording of check-in and eviction dates
    for convenient access to them 
    :type: date_buffer: date object
    :param: date_flag: the 'switch' attribute, for redirection entered dates to the corresponding
    handlers (check_in or check_out) 
    :type: date_flag: bool
    :param: zero_condition: the state from the moment when the bot is turned on to the display of the 
    keyboard with the found cities 
    :type: zero_condition: bool
    :param: first_condition: the state from the moment when keyboard with the found cities is displayed
    until the "differance_between_commands" function from handlers_before_request is called
    :type: first_condition: bool
    :param: second_condition: the state from the moment the "differance_between_commands" function 
    from the handlers_before_request is called until the "check_out" function from handlers_before_request 
    is called
    :type: second_condition: bool
    :param: third_condition: the state from the moment the "check_out" function from handlers_before_request 
    is called until the "gets_main_hotels_data" function from handlers_for_request_and_after is called 
    :type: third_condition: bool
    :param: intermediate_condition: the state from the moment when "gets_main_hotels_data" function 
    from handlers_for_request_and_after is called until "no_answer_about_photo" or "yes_answer_about_photo"
    (from handlers_before_request) or "delete_showed_hotels" from handlers_for_request_and_after are called
    :type: intermediate_condition: bool 
    :param: fourth_condition: the state from the moment the when "no_answer_about_photo" or "yes_answer_about_photo"
    (from handlers_before_request) or "delete_showed_hotels" from handlers_for_request_and_after are called until
    "show_more_hotels_if_there_are_available_variants" from the keyboards.inline is called
    :type: fourth_condition: bool 
    :param: continue_searching: the state from the moment the when "delete_showed_hotels" from 
    handlers_for_request_and_after is called until "result_waiting" from handlers_before_request is called 
    (the second time) or "show_more_hotels_if_there_are_available_variants" from keyboards.inline is called
    :type: continue_searching: bool 
    :param: fifth_condition: the state from the  display of the required number 
    ("show_more_hotels_if_there_are_available_variants" function from keyboards.inline is called) until 
    "delete_showed_hotels" from handlers_for_request_and_after is called or the end of the script execution 
    :type: fifth_condition: bool 
    :param: next_function: the name of the function in the function chain that will be called 
    next
    :type: next_function: string
    :param: id_message_for_delete: the message id with inline keyboard, subject to deletion, 
    in the case it has not been used
    :type: id_message_for_delete: string
    :param: delete_message: the presence of the message that can be deleted 
    :type: delete_message: bool
    :param: current_buffer: When call the API for the first time: contains the cities which were found. 
    When call the  API for the second time: contains hotels which were found by destination_id. 
    :type: current_buffer: list of dictionaries or ordered dictionary
    :param: connect_attempt: number of API call attempts made 
    :type: connect_attempt: integer
    :param: start_from_the_beginning_if_there_is_something_to_show: the display of the specified 
    number of hotels has been made
    :type: start_from_the_beginning_if_there_is_something_to_show: bool
    :param: start_from_the_beginning_if_nothing_to_show: no more hotels were found 
    according to the specified parameters
    :type: start_from_the_beginning_if_nothing_to_show: bool
    """""

    all_users: dict = dict()

    def __init__(self):
        self.user_name: str is None
        self.current_command: str is None
        self.city: str is None
        self.hotels_count: int is None
        self.hotel_id: str is None
        self.current_hotel_index: int is None
        self.destination_id: str is None
        self.answer_about_photo: str is None
        self.photo_count: int is None
        self.adults_count: str is None
        self.check_in: date is None
        self.check_out: date is None
        self.minimum_price: int is None
        self.maximum_price: int is None
        self.minimum_distance: int is None
        self.maximum_distance: int is None
        self.date_buffer: date is None
        self.date_flag: bool = False
        self.zero_condition: bool = True
        self.first_condition: bool = False
        self.second_condition: bool = False
        self.third_condition: bool = False
        self.intermediate_condition: bool = False
        self.fourth_condition: bool = False
        self.continue_searching = False
        self.fifth_condition: bool = False
        self.next_function: str is None
        self.id_message_for_delete: str is None
        self.delete_message: bool = False
        self.current_buffer: Optional[List[Dict], OrderedDict[str, Dict]] is None
        self.connect_attempt: int = 0
        self.start_from_the_beginning_if_there_is_something_to_show: bool = False
        self.start_from_the_beginning_if_nothing_to_show: bool = False

    @staticmethod
    def get_user(chat_id):
        """Accepts a unique chat ID with the user as a key and returns the user
         object from the dictionary, if such exists, either creates a new one,
         adds it to the dictionary and also returns from there

        :param: chat_id: id of the user's chat
        :type: chat_id: string
        :return: an object of the User data-class
        :rtype: User object"""

        if UserData.all_users.get(chat_id) is None:
            UserData.all_users[chat_id] = UserData()
        return UserData.all_users.get(chat_id)

    def clear_all(self):
        """Updates the values of all dynamic attributes of the user data-class object
    and sets the value to None or bool (the value of user_name remains unchanged, for the subsequent
    correct operation of the bot)"""

        for i_elem in self.__dict__:
            if i_elem == 'date_flag':
                self.__dict__[i_elem] = False
            elif i_elem == 'user_name':
                self.__dict__[i_elem] = self.__dict__[i_elem]
            elif i_elem == 'zero_condition':
                self.__dict__[i_elem] = True
            elif i_elem == 'first_condition':
                self.__dict__[i_elem] = False
            elif i_elem == 'second_condition':
                self.__dict__[i_elem] = False
            elif i_elem == 'third_condition':
                self.__dict__[i_elem] = False
            elif i_elem == 'intermediate_condition':
                self.__dict__[i_elem] = False
            elif i_elem == 'fourth_condition':
                self.__dict__[i_elem] = False
            elif i_elem == 'fifth_condition':
                self.__dict__[i_elem] = False
            elif i_elem == 'delete_message':
                self.__dict__[i_elem] = False
            elif i_elem == 'connect_attempt':
                self.__dict__[i_elem] = 0
            elif i_elem == 'start_from_the_beginning_if_there_is_something_to_show':
                self.__dict__[i_elem] = False
            elif i_elem == 'start_from_the_beginning_if_nothing_to_show':
                self.__dict__[i_elem] = False
            elif i_elem == 'continue_searching':
                self.__dict__[i_elem] = False
            else:
                self.__dict__[i_elem] = None
