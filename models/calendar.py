from telegram_bot_calendar import DetailedTelegramCalendar


class MyTranslationCalendar(DetailedTelegramCalendar):
    """Custom calendar class

    :param: days_of_week:  list with the names of the days of the week
    :type: days_of_week: list with strings
    :param: month:  list with the names of the months
    :type: month: list with srings
    :param: prev_button: previous button
    :type: prev_button: string
    :param: next_button: next button
    :type: next_button: string
    :param: my_LSTEP: dictionary with year, month and day as value
    and y, m,d as key
    :type: my_LSTEP: dictionary with strings as key and value"""

    prev_button = "⬅️"
    next_button = "➡️"
    my_LSTEP = {
        'y': 'Год',
        'm': 'Месяц',
        'd': 'День'
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.days_of_week['ru'] = [
            'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Cб', 'Вс'
        ]
        self.months['ru'] = [
            'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август',
            'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
        ]
