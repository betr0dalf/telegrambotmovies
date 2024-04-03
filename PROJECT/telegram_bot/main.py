import telebot
from telebot import types

bot = telebot.TeleBot('7008011432:AAGzB8Njxp2C8LwxjOCMEh2PomlK-DHIyp4')


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    button1 = types.KeyboardButton('Искать фильм 🍿')
    button2 = types.KeyboardButton('Топ фильмов по жанру 🎥')
    button3 = types.KeyboardButton('Топ фильмы за год 🔥')
    button4 = types.KeyboardButton('Топ фильмы режиссера 🎬')
    button5 = types.KeyboardButton('Топ фильмы актёра 🌟')
    markup.row(button1)
    markup.row(button2, button3)
    markup.row(button4, button5)

    bot.send_message(message.chat.id, f'Здравствуй, {message.from_user.first_name} {message.from_user.last_name}!',
                     reply_markup=markup)

    bot.register_next_step_handler(message, on_click)


def on_click(message):
    if message.text == 'Искать фильм 🍿':
        bot.send_message(message.chat.id, 'work in progress...')
    elif message.text == 'Топ фильмов по жанру 🎥':
        bot.send_message(message.chat.id, 'work in progress...')
    elif message.text == 'Топ фильмы за год 🔥':
        bot.send_message(message.chat.id, 'work in progress...')
    elif message.text == 'Топ фильмы режиссера 🎬':
        bot.send_message(message.chat.id, 'work in progress...')
    elif message.text == 'Топ фильмы актёра 🌟':
        bot.send_message(message.chat.id, 'work in progress...')


bot.polling(none_stop=True)
