from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from My_bot_3 import bot


def start(m):
    calendar, step = DetailedTelegramCalendar(calendar_id=1).build()
    bot.send_message(m.chat.id,
                     f"Укажите дату заезда {LSTEP[step]}",
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
    result, key, step = DetailedTelegramCalendar().process(c.data)
    if not result and key:
        bot.edit_message_text(f"Select {LSTEP[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"You selected {result}",
                              c.message.chat.id,
                              c.message.message_id)


ALL_STEPS = {'y': 'год', 'm': 'месяц', 'd': 'день'} #чтобы русифицировать сообщения

