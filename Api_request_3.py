import requests


def api_request(method_endswith,  # Меняется в зависимости от запроса. locations/v3/search либо properties/v2/list
                params,  # Параметры, если locations/v3/search, то {'q': 'Рига', 'locale': 'ru_RU'}
                method_type  # Метод\тип запроса GET\POST
                ):
    url = f"https://hotels4.p.rapidapi.com/{method_endswith}"

    # В зависимости от типа запроса вызываем соответствующую функцию
    if method_type == 'GET':
        return get_request(
            url=url,
            params=params
        )
    else:
        return post_request(
            url=url,
            params=params
        )


def get_request(url, params):
    """
    Получаем GET запрос с API
    :param url: https://hotels4.p.rapidapi.com/
    :param params: Headers
    :return:
    """
    try:
        response = requests.get(
            url,
            headers={
                "X-RapidAPI-Key": "cbc6bd4bf0msh0520f4547b340f3p1cbd85jsn9278b865e9ea",
                "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
            },
            params=params,
            timeout=25
        )
        if response.status_code == requests.codes.ok:
            data = response.json()
            return data

    except Exception as ex:
        print(ex)


def post_request(url, params):
    """
    Получаем POST запрос с API
    :param url: https://hotels4.p.rapidapi.com/
    :param params: Headers
    :return:
    """
    try:
        response = requests.post(
            url,
            headers={
                "content-type": "application/json",
                "X-RapidAPI-Key": "cbc6bd4bf0msh0520f4547b340f3p1cbd85jsn9278b865e9ea",
                "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
            },
            json=params,
            timeout=25
        )
        if response.status_code == requests.codes.ok:
            data = response.json()
            return data
    except Exception as ex:
        print(ex)


def get_list_name_city(city: str):
    """
    Пользователь вводит название города в виде строки.
    В результате получаем список городов мира, соответствующих названию.
    :param city: название города
    :return: список городов мира с соответствующим названием
    """
    list_city = api_request("locations/v3/search", {"q": city, "locale": "ru_RU"}, "GET")
    data = dict(list_city)
    result_name = [elem["regionNames"]['fullName'] for elem in data["sr"] if elem["type"] == "CITY"]
    return result_name


def get_id(city: str):
    """
    В качестве аргумента указывается полное название города, полученное из функции get_list_name_city.
    В результате получаем ID выбранного города
    :param city:
    :return:
    """
    list_city = api_request("locations/v3/search", {"q": f"{city}", "locale": "ru_RU"}
                            , "GET")
    data = dict(list_city)
    result_id = [elem["gaiaId"] for elem in data["sr"] if elem["type"] == "CITY"]
    result_name = [elem["regionNames"]['fullName'] for elem in data["sr"]if elem["type"] == "CITY"]
    result_dict = dict(zip(result_name, result_id))
    result = result_dict[city]
    return result


def get_address(id_hotel):
    request_address = api_request('properties/v2/detail', {"currency": "USD", "eapid": 1, "locale": "ru_RU",
                                                           "siteId": 300000001, "propertyId": f"{id_hotel}"}, "POST")
    data = dict(request_address)
    address_line = data["data"]["propertyInfo"]["summary"]["location"]["address"]["addressLine"]
    return address_line
