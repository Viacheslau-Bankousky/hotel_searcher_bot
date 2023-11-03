from datetime import datetime

from peewee import (CharField, SqliteDatabase,
                    DateTimeField, Model, TextField, ForeignKeyField)

db = SqliteDatabase('./database/hotels.db')


class BaseModel(Model):
    """The base class from which all tables inherit
    current database"""

    class Meta:
        """A class with database metadata

        :param: db: current database
        :type: db: database object"""

        database = db


class User(BaseModel):
    """User model

    :param: chat_id: the unique ID of the user's chat
    :type: chat_id: CharField"""

    chat_id = CharField()


class HotelSearch(BaseModel):
    """"The model containing search results

    :param: users_information: the foreign key field for linking to the user table
    :type: users_information: ForeignKeyField
    :param: command: the current entered command
    :type: command: CharField
    :param: date_of_command: date and time when the command was used (default value)
    :type: date_of_command: DateTime
    :param: result_of_command: results of the commands used
    :type: result_of_command: TextField

    """
    users_information = ForeignKeyField(User)
    command = CharField()
    date_of_command = DateTimeField(default=datetime.now)
    result_of_command = TextField()
