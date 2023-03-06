from telebot.handler_backends import State, StatesGroup


class LowPrice(StatesGroup):
    name_city = State()
    id_city = State()
    count_hotel = State()
    need_photo = State()
    count_photo = State()
    id_hotel = State()
    name_city_from_list = State()
    check_in = State()
    check_out = State()
    photo = State()
    sort = State()
    min_price = State()
    max_price = State()
    min_distance = State()
    max_distance = State()
