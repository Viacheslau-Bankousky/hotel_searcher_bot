import functools
from copy import deepcopy
from typing import Callable, Any

from loguru import logger
from telebot.types import Message

from models.data_class import UserData

logger.add('./logger/log_file.log', rotation='100 MB', retention='1 day')


def logger_wraps(*, entry=True, exit=True, level="DEBUG") -> Callable:
    """Decorates functions by adding information about their call, passed parameters
    and exit from them

    :param: entry: starting the decorator when the function is started
    :type: entry: bool
    :param: exit: shutdown of the decorator after exiting the function
    :type: exit: bool
    :param: level: level of logger's severity
    :type: level: string
    :return: any called function to which a decorator has been applied
    :rtype: Callable"""

    def wrapper(function) -> Callable:
        """External wrapper for called functions

        :param: function: called functions
        :type: function: Callable
        """

        name: str = function.__name__

        @functools.wraps(function)
        def wrapped(*args, **kwargs) -> Any:
            """Internal wrapper for called function

            :param: args: any positional arguments:
            :type: args: Tuple[Any]
            :param: kwargs: any keyword arguments
            :type: kwargs: Dictionary[Any, Any]
            :return: result of called function
            :rtype: Any"""

            logger_ = logger.opt(depth=1)

            if entry:
                enter_to_function(additional_logger=logger_,
                                  level=level,
                                  function_name=name,
                                  args=args, kwargs=kwargs)

            result = function(*args, **kwargs)
            if exit:
                exit_from_function(additional_logger=logger_,
                                   level=level,
                                   function_name=name,
                                   result=result,
                                   args=args, kwargs=kwargs)
            return result

        return wrapped

    return wrapper


def enter_to_function(additional_logger: logger, level: str, function_name: str,
                      args, kwargs) -> None:
    """Transforms the format for displaying logger messages when the called function is started

    :param: additional_logger: additional logger for correct operations
    :type: additional_logger: logger
    :param: level: level of logger's severity
    :type: level: string
    :param: function_name: the name of called function
    :type: string
    :param: args: any positional arguments:
    :type: args: Tuple[Any]
    :param: kwargs: any keyword arguments
    :type: kwargs: Dictionary[Any, Any]
    :return: None
    """

    if len(args) > 0 and isinstance(args[0], Message):
        additional_logger.log(level, "{} is entering '{}' (args={}, kwargs={})",
                              UserData.get_user(args[0].chat.id).user_name,
                              function_name, args, kwargs)
    elif len(kwargs) > 0 and isinstance(kwargs['message'], Message):
        additional_logger.log(level, "{} is entering '{}' (args={}, kwargs={})",
                              UserData.get_user(kwargs['message'].chat.id).user_name,
                              function_name, args, kwargs)
    else:
        additional_logger.log(level, "Entering '{}' (args={}, kwargs={})",
                              function_name, args, kwargs)


def exit_from_function(additional_logger: logger, level: str, function_name: str,
                       result, args, kwargs) -> None:
    """Transforms the format for displaying logger messages when the called function is ended.
    The display format eliminates the leakage of confidential information

    :param: additional_logger: additional logger for correct operations
    :type: additional_logger: logger
    :param: level: level of logger's severity
    :type: level: string
    :param: function_name: the name of called function
    :type: string
    :param: result: the result of the called function
    :type: result: Any
    :param: args: any positional arguments:
    :type: args: Tuple[Any]
    :param: kwargs: any keyword arguments
    :type: kwargs: Dictionary[Any, Any]
    :return: None
    """

    result_ = deepcopy(result)
    if isinstance(result, tuple) and len(result) > 1 and (
            'X-RapidAPI-Key' in list(result[0].keys())):
        result_[0]['X-RapidAPI-Key'] = 'XXX'

    if function_name == 'create_text_message':
        result_ = 'there should be a message text'

    if len(args) > 0 and isinstance(args[0], Message):
        additional_logger.log(level, "{} is exiting '{}' (result={})",
                              UserData.get_user(args[0].chat.id).user_name,
                              function_name, result_)
    elif len(kwargs) > 0 and isinstance(kwargs['message'], Message):
        additional_logger.log(level, "{} is exiting '{}' (result={})",
                              UserData.get_user(kwargs['message'].chat.id).user_name,
                              function_name, result_)
    else:
        additional_logger.log(level, "Exiting '{}' (result={})", function_name, result_)
