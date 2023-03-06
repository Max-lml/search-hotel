from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from Api_request_3 import get_list_name_city


def response_photo() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(True, True)
    keyboard.add(KeyboardButton('Да'))
    keyboard.add(KeyboardButton('Нет'))
    return keyboard


def response_cities(city) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(True, True)
    for i in range(len(get_list_name_city(city))):
        keyboard.add(KeyboardButton(get_list_name_city(city)[i]))
    return keyboard

