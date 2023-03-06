from datetime import datetime, date
from Keyboards_3 import *
from State_3 import LowPrice
from Config_3 import BOT_TOKEN
from Lowhigh_price import *
from Bestdeal import *
import telebot
from telebot import types
from Calendare import *
from telebot.types import Message
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP


bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def sort(message: Message) -> None:
    bot.send_message(message.from_user.id, 'hello')


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def sort(message: Message) -> None:
    bot.send_message(message.from_user.id, f'Итак, Приступаем к поиску, укажи город: ')
    bot.set_state(message.from_user.id, LowPrice.name_city, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['sort'] = message.text
    # with open('history.txt', 'w') as file:
    #     file.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n Выбрана команда {data["sort"]}')


@bot.message_handler(state=LowPrice.name_city)
def get_name_city(message: Message) -> None:
    if message.text.isalpha():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['name_city'] = message.text
        bot.send_message(message.from_user.id, f'Выберите из списка',
                         reply_markup=response_cities(data['name_city']))
        bot.set_state(message.from_user.id, LowPrice.name_city_from_list, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Название города может содержать только буквы')


@bot.message_handler(state=LowPrice.name_city_from_list)
def get_city_name_list(message: Message) -> None:
    calendar, step = DetailedTelegramCalendar(calendar_id=1, min_date=date.today(), locale='ru').build()
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['name_city_from_list'] = message.text
        data['id_city'] = get_id(data['name_city_from_list'])
    bot.send_message(message.from_user.id, f"Укажите дату прибытия")
    bot.send_message(message.from_user.id, f"Select {LSTEP[step]}",
                     reply_markup=calendar)
    bot.set_state(message.from_user.id, LowPrice.check_out, message.chat.id)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def check_in(c):
    result, key, step = DetailedTelegramCalendar(calendar_id=1, min_date=date.today()).process(c.data)
    if not result and key:
        bot.edit_message_text(f"Select {LSTEP[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"{result}",
                              c.message.chat.id,
                              c.message.message_id)
        calendar, step = DetailedTelegramCalendar(calendar_id=2, min_date=result, locale='ru').build()
        bot.send_message(c.from_user.id, f"Укажите дату выезда")
        bot.send_message(c.from_user.id, f"Select {LSTEP[step]}",
                         reply_markup=calendar)
        with bot.retrieve_data(c.from_user.id, c.message.chat.id) as data:
            data['check_in'] = result


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def check_out(c):
    result, key, step = DetailedTelegramCalendar(calendar_id=2, min_date=date.today()).process(c.data)
    if not result and key:
        bot.edit_message_text(f"Select {LSTEP[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"{result}",
                              c.message.chat.id,
                              c.message.message_id)
        with bot.retrieve_data(c.from_user.id, c.message.chat.id) as data:
            data['check_out'] = result

        bot.send_message(c.from_user.id, f"Сколько отелей вывести?")


@bot.message_handler(state=LowPrice.check_out)
def get_count_hotels(message: Message) -> None:
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['count_hotel'] = message.text
        bot.send_message(message.from_user.id, f'{data["count_hotel"]} отеля. Нужны ли фото?',
                         reply_markup=response_photo())
        bot.set_state(message.from_user.id, LowPrice.need_photo, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Какая то проблема')


@bot.message_handler(state=LowPrice.need_photo)
def get_need_photo(message: Message) -> None:
    if message.text == 'Да':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['need_photo'] = message.text
            bot.send_message(message.from_user.id, 'Сколько фото вывести для каждого отеля?(от 2 до 5)')
        bot.set_state(message.from_user.id, LowPrice.count_photo, message.chat.id)
    elif message.text == 'Нет':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['need_photo'] = message.text
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                bot.send_message(
                    message.from_user.id, f"Вы выбрали: \nName: {data['name_city_from_list']}\n"
                                          f"ID: {data['id_city']}\n"
                                          f"Check_in: {data['check_in']}\n"
                                          f"Check_out : {data['check_out']}\n"
                                          f"Count_hotels: {data['count_hotel']}\n"
                                          f"Sort: {data['sort']}"
                                          )
            if data['sort'] == '/lowprice':
                bot.send_message(message.from_user.id, 'Загружаю информацию...')
                result = get_hotel_info_low_high(city_id=data['id_city'], count_result=data['count_hotel'],
                                                 day_in=int(data['check_in'].strftime('%d')),
                                                 month_in=int(data['check_in'].strftime('%m')),
                                                 year_in=int(data['check_in'].strftime('%y')),
                                                 day_out=int(data['check_out'].strftime('%d')),
                                                 month_out=int(data['check_out'].strftime('%m')),
                                                 year_out=int(data['check_out'].strftime('%y')),
                                                 sort="PRICE_LOW_TO_HIGH", count_photo=0
                                                 )
                for info in result[0]:
                    bot.send_message(message.from_user.id, info)
                    with open('history.txt', 'a') as file:
                        file.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
                                   f'\n Результат запроса: {info}')
            elif data['sort'] == '/highprice':
                bot.send_message(message.from_user.id, 'Загружаю информацию...')
                result = get_hotel_info_low_high(city_id=data['id_city'], count_result=data['count_hotel'],
                                                 day_in=int(data['check_in'].strftime('%d')),
                                                 month_in=int(data['check_in'].strftime('%m')),
                                                 year_in=int(data['check_in'].strftime('%y')),
                                                 day_out=int(data['check_out'].strftime('%d')),
                                                 month_out=int(data['check_out'].strftime('%m')),
                                                 year_out=int(data['check_out'].strftime('%y')),
                                                 sort="PRICE_HIGH_TO_LOW", count_photo=0
                                                 )
                for info in result[0]:
                    bot.send_message(message.from_user.id, info)
                    with open('history.txt', 'a') as file:
                        file.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
                                   f'\n Результат запроса: {info}')
            elif data['sort'] == '/bestdeal':
                bot.send_message(message.from_user.id, 'Укажите минимальную цену за ночь')
                bot.set_state(message.from_user.id, LowPrice.min_price, message.chat.id)


@bot.message_handler(state=LowPrice.count_photo)
def get_count_photo(message: Message) -> None:
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['count_photo'] = message.text
            bot.send_message(
            message.from_user.id, f"Вы выбрали: \nName: {data['name_city_from_list']}\n"
                                  f"ID: {data['id_city']}\n"
                                  f"Check_in: {data['check_in']}\n"
                                  f"Check_out : {data['check_out']}\n"
                                  f"Need_photo: {data['need_photo']}\n"
                                  f"Count_hotels: {data['count_hotel']}\n"
                                  f"Count_photo: {data['count_photo']}\n"
                                  f"Sort: {data['sort']}"
            )
            if data['sort'] == '/lowprice':
                bot.send_message(message.from_user.id, 'Загружаю информацию...')
                result = get_hotel_info_low_high(city_id=data['id_city'], count_result=int(data['count_hotel']),
                                                 day_in=int(data['check_in'].strftime('%d')),
                                                 month_in=int(data['check_in'].strftime('%m')),
                                                 year_in=int(data['check_in'].strftime('%y')),
                                                 day_out=int(data['check_out'].strftime('%d')),
                                                 month_out=int(data['check_out'].strftime('%m')),
                                                 year_out=int(data['check_out'].strftime('%y')),
                                                 sort="PRICE_LOW_TO_HIGH",
                                                 count_photo=int(data['count_photo'])
                                                 )
                count = 0
                for info in result[0]:
                    bot.send_message(message.from_user.id, info)
                    with open('history.txt', 'a') as file:
                        file.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
                                   f'\n Результат запроса: {info}')
                    media = [types.InputMediaPhoto(elem) for elem in result[1][count]]
                    bot.send_media_group(message.from_user.id, media)
                    count += 1

            elif data['sort'] == '/highprice':
                bot.send_message(message.from_user.id, 'Загружаю информацию...')
                result = get_hotel_info_low_high(city_id=data['id_city'], count_result=int(data['count_hotel']),
                                                 day_in=int(data['check_in'].strftime('%d')),
                                                 month_in=int(data['check_in'].strftime('%m')),
                                                 year_in=int(data['check_in'].strftime('%y')),
                                                 day_out=int(data['check_out'].strftime('%d')),
                                                 month_out=int(data['check_out'].strftime('%m')),
                                                 year_out=int(data['check_out'].strftime('%y')),
                                                 sort="PRICE_HIGH_TO_LOW",
                                                 count_photo=int(data['count_photo'])
                                                 )
                count = 0
                for info in result[0]:
                    bot.send_message(message.from_user.id, info)
                    with open('history.txt', 'a') as file:
                        file.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
                                   f'\n Результат запроса: {info}')
                    media = [types.InputMediaPhoto(elem) for elem in result[1][count]]
                    bot.send_media_group(message.from_user.id, media)
                    count += 1
            elif data['sort'] == '/bestdeal':
                bot.send_message(message.from_user.id, 'Укажите минимальную цену за ночь')
                bot.set_state(message.from_user.id, LowPrice.min_price, message.chat.id)
            else:
                bot.send_message(message.from_user.id, 'Какая то проблема')


@bot.message_handler(state=LowPrice.min_price)
def get_min_price(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['min_price'] = message.text
    bot.send_message(message.from_user.id, 'Укажите максимальную цену за ночь')
    bot.set_state(message.from_user.id, LowPrice.max_price, message.chat.id)


@bot.message_handler(state=LowPrice.max_price)
def get_max_price(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['max_price'] = message.text
    bot.send_message(message.from_user.id, 'Укажите минимальное расстояние от центра города')
    bot.set_state(message.from_user.id, LowPrice.min_distance, message.chat.id)


@bot.message_handler(state=LowPrice.min_distance)
def get_min_distance(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['min_distance'] = message.text
    bot.send_message(message.from_user.id, 'Укажите максимальное расстояние от центра города')
    bot.set_state(message.from_user.id, LowPrice.max_distance, message.chat.id)


@bot.message_handler(state=LowPrice.max_distance)
def get_max_distance(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['max_distance'] = message.text
    bot.send_message(
        message.from_user.id, f"Вы выбрали: \nName: {data['name_city_from_list']}\n"
                              f"ID: {data['id_city']}\n"
                              f"Check_in: {data['check_in']}\n"
                              f"Check_out : {data['check_out']}\n"
                              f"Need_photo: {data['need_photo']}\n"
                              f"Count_hotels: {data['count_hotel']}\n"
                              f"Sort: {data['sort']}\n"
                              f"Min Price: {data['min_price']}\n"
                              f"Max Price: {data['max_price']}\n"
                              f"Min distance: {data['min_distance']}\n"
                              f"Max distance: {data['max_distance']}\n"
    )
    if data['need_photo'] == 'Да':
        bot.send_message(message.from_user.id, 'Загружаю информацию...')
        result = bestdeal(city_id=data['id_city'], count_result=int(data['count_hotel']),
                          day_in=int(data['check_in'].strftime('%d')),
                          month_in=int(data['check_in'].strftime('%m')),
                          year_in=int(data['check_in'].strftime('%y')),
                          day_out=int(data['check_out'].strftime('%d')),
                          month_out=int(data['check_out'].strftime('%m')),
                          year_out=int(data['check_out'].strftime('%y')),
                          sort="PRICE_LOW_TO_HIGH", min_price=int(data['min_price']),
                          max_price=int(data['max_price']),
                          min_distance=int(data['min_distance']),
                          max_distance=int(data['max_distance']), count_photo=int(data['count_photo'])
                          )
        count = 0
        for info in result[0]:
            bot.send_message(message.from_user.id, info)
            with open('history.txt', 'a') as file:
                file.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
                           f'\n Результат запроса: {info}')
            media = [types.InputMediaPhoto(elem) for elem in result[1][count]]
            bot.send_media_group(message.from_user.id, media)
            count += 1
    elif data['need_photo'] == 'Нет':
        bot.send_message(message.from_user.id, 'Загружаю информацию...')
        result = bestdeal(city_id=data['id_city'], count_result=int(data['count_hotel']),
                          day_in=int(data['check_in'].strftime('%d')),
                          month_in=int(data['check_in'].strftime('%m')),
                          year_in=int(data['check_in'].strftime('%y')),
                          day_out=int(data['check_out'].strftime('%d')),
                          month_out=int(data['check_out'].strftime('%m')),
                          year_out=int(data['check_out'].strftime('%y')),
                          sort="PRICE_LOW_TO_HIGH", min_price=int(data['min_price']),
                          max_price=int(data['max_price']),
                          min_distance=int(data['min_distance']),
                          max_distance=int(data['max_distance']), count_photo=0
                          )
        for info in result[0]:
            bot.send_message(message.from_user.id, info)
            with open('history.txt', 'a') as file:
                file.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
                           f'\n Результат запроса: {info}')


@bot.message_handler(commands=['test'])
def name_city_list(message: Message) -> None:
    result = bestdeal(city_id=3023, count_result=2,
                      day_in=1,
                      month_in=2,
                      year_in=2023,
                      day_out=10,
                      month_out=2,
                      year_out=2023,
                      sort="PRICE_LOW_TO_HIGH", min_price=10,
                      max_price=1000, min_distance=0,
                      max_distance=9, count_photo=2
                      )
    count = 0
    for info in result[0]:
        bot.send_message(message.from_user.id, info)
        media = [types.InputMediaPhoto(elem) for elem in result[1][count]]
        bot.send_media_group(message.from_user.id, media)
        count += 1


bot.polling(none_stop=True)

