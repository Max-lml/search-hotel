import random
from Api_request_3 import *


def get_hotel_info_low_high(city_id: int, count_result: int, day_in: int, month_in: int, year_in: int,
                   day_out: int, month_out: int, year_out: int, sort:str, count_photo: int
                   ):
    """
    Функция выводит список отелей в указанном городе с данными: Название отеля, ID Отеля,
    Расстояние от центра, Цена за ночь, Цена за весь срок
    :param city_id: ID города
    :param count_result: количество выводимых отелей
    :param count_photo: количество фото к каждому отелю
    :return:
    """
    list_hotels = api_request("properties/v2/list",
                              {"currency": "USD",	"eapid": 1,	"locale": "ru_RU", "siteId": 300000001,
                               "destination": {"regionId": f'{city_id}'},
                               "checkInDate": {"day": day_in, "month": month_in, "year": year_in},
                               "checkOutDate": {"day": day_out, "month": month_out, "year": year_out},
                               "rooms": [{"adults": 2, "children": [{"age": 5}, {"age": 7}]}],
                               "resultsStartingIndex": 0,	"resultsSize": 30,	"sort": sort,
                               "filters": {"price": {"max": 3000, "min": 20}}}, "POST")

    data = dict(list_hotels)
    result_name_hotels = [elem['name'] for elem in data["data"]["propertySearch"]["properties"]]
    price_day = [elem["price"]["lead"]["amount"] for elem in data["data"]["propertySearch"]["properties"]]
    id_hotels = [elem['id'] for elem in data["data"]["propertySearch"]["properties"]]
    distance_from_destination = [elem["destinationInfo"]['distanceFromDestination']["value"]
                                 for elem in data["data"]["propertySearch"]["properties"]]
    all_result = []
    photo = []
    if count_photo != 0:
        for i in range(len(result_name_hotels)):
            all_result.append(f'Название отеля: {result_name_hotels[i]}\n'
                              f'ID Отеля: {id_hotels[i]}\n'
                              f'Расстояние от центра: {float(distance_from_destination[i])}\n'
                              f'Цена за ночь: {round(price_day[i], 2)}$\n'
                              f'Цена за весь срок: {round(price_day[i] * (day_out - day_in), 2)}$\n')
            photo.append(get_photo(id_hotels[i], count_photo))
        return [all_result[: count_result], photo[: count_result]]

    else:
        for i in range(len(result_name_hotels)):
            all_result.append(f'Название отеля: {result_name_hotels[i]}\n'
                              f'ID Отеля: {id_hotels[i]}\n'
                              f'Расстояние от центра: {float(distance_from_destination[i])}\n'
                              f'Цена за ночь: {round(price_day[i], 2)}$\n'
                              f'Цена за весь срок: {round(price_day[i] * (day_out - day_in), 2)}$\n')
        return [all_result[: int(count_result)]]


def get_address(id_hotel):
    request_address = api_request('properties/v2/detail', {"currency": "USD", "eapid": 1, "locale": "ru_RU",
                                                           "siteId": 300000001, "propertyId": f"{id_hotel}"}, "POST")
    data = dict(request_address)
    address_line = data["data"]["propertyInfo"]["summary"]["location"]["address"]["addressLine"]
    return address_line


def get_photo(id_hotel, count_photo):
    request_photo = api_request('properties/v2/detail', {"currency": "USD", "eapid": 1, "locale": "ru_RU",
                                                         "siteId": 300000001, "propertyId": f"{id_hotel}"}, "POST")
    data = request_photo
    photo = [elem["image"]["url"] for elem in data["data"]["propertyInfo"]["propertyGallery"]["images"]]
    return random.sample(photo, count_photo)