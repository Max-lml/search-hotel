from Api_request_3 import *
import random



def bestdeal(city_id: int, count_result: int, day_in: int, month_in: int, year_in: int,
                   day_out: int, month_out: int, year_out: int, sort, min_price: int, max_price: int,
                   min_distance:float, max_distance:float, count_photo: int
                   ):
    """
    Функция выводит список отелей в указанном городе с данными: Название отеля, ID Отеля,
    Расстояние от центра, Цена за ночь, Цена за весь срок
    :param city_id: ID города
    :param count_result: количество выводимых отелей
    :param count_photo: количество фото к каждому отелю
    :return:
    """
    try:
        list_hotels = api_request("properties/v2/list",
                                  {"currency": "USD",	"eapid": 1,	"locale": "ru_RU", "siteId": 300000001,
                                   "destination": {"regionId": f'{city_id}'},
                                   "checkInDate": {"day": day_in, "month": month_in, "year": year_in},
                                   "checkOutDate": {"day": day_out, "month": month_out, "year": year_out},
                                   "rooms": [{"adults": 2, "children": [{"age": 5}, {"age": 7}]}],
                                   "resultsStartingIndex": 0,	"resultsSize": 30,	"sort": sort,
                                   "filters": {"price": {"max": max_price, "min": min_price}}}, "POST")

        data = dict(list_hotels)
        result_name_hotels = [
            elem['name'] for elem in data["data"]["propertySearch"]["properties"]
            if elem["price"]["lead"]["amount"] >= min_price
            and elem["price"]["lead"]["amount"] <= max_price
            and elem["destinationInfo"]['distanceFromDestination']["value"] >= min_distance
            and elem["destinationInfo"]['distanceFromDestination']["value"] <= max_distance]
        price_day = [elem["price"]["lead"]["amount"] for elem in data["data"]["propertySearch"]["properties"]
                     if elem["price"]["lead"]["amount"] >= min_price
                     and elem["price"]["lead"]["amount"] <= max_price
                     and elem["destinationInfo"]['distanceFromDestination']["value"] >= min_distance
                     and elem["destinationInfo"]['distanceFromDestination']["value"] <= max_distance]
        id_hotels = [elem['id'] for elem in data["data"]["propertySearch"]["properties"]if
                     elem["price"]["lead"]["amount"] >= min_price
                     and elem["price"]["lead"]["amount"] <= max_price
                     and elem["destinationInfo"]['distanceFromDestination']["value"] >= min_distance and
                     elem["destinationInfo"]['distanceFromDestination']["value"] <= max_distance]
        distance_from_destination = [
            elem["destinationInfo"]['distanceFromDestination']["value"] for elem in data["data"]["propertySearch"]
            ["properties"] if elem
            ["price"]["lead"]["amount"] >= min_price
            and elem["price"]["lead"]["amount"] <= max_price and elem["destinationInfo"]
            ['distanceFromDestination']["value"] >= min_distance and
            elem["destinationInfo"]['distanceFromDestination']["value"] <= max_distance
        ]
        all_result = []
        photo = []
        if count_photo != 0:
            for i in range(len(result_name_hotels)):
                all_result.append(f'Название отеля: {result_name_hotels[i]}\n'
                                  f'ID Отеля: {id_hotels[i]}\n'
                                  f'Расстояние от центра: {float(distance_from_destination[i])}км\n'
                                  f'Цена за ночь: {round(price_day[i], 2)}$\n'
                                  f'Цена за весь срок: {round(price_day[i]*(day_out-day_in), 2)}$\n'
                                  f' Адрес: {get_address(id_hotels[i])}\n'
                                  )
                photo.append(get_photo(id_hotels[i], count_photo))
            return [all_result[: count_result], photo[: count_result]]
        else:
            for i in range(len(result_name_hotels)):
                all_result.append(f'Название отеля: {result_name_hotels[i]}\n'
                                  f'ID Отеля: {id_hotels[i]}\n'
                                  f'Расстояние от центра: {float(distance_from_destination[i])}км\n'
                                  f'Цена за ночь: {round(price_day[i], 2)}$\n'
                                  f'Цена за весь срок: {round(price_day[i]*(day_out-day_in), 2)}$\n'
                                  f' Адрес: {get_address(id_hotels[i])}\n'
                                  )
            return [all_result[: count_result]]

    except Exception as ex:
        print(ex)


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


a = bestdeal(city_id=3023, count_result=2,
             day_in=10,
             month_in=2,
             year_in=2023,
             day_out=20,
             month_out=2,
             year_out=2023,
             sort="PRICE_LOW_TO_HIGH", min_price=10,
             max_price=1000, min_distance=0,
             max_distance=9, count_photo=2
             )