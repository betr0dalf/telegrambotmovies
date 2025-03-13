import telebot
from telebot import types
import pandas as pd
from background import keep_alive

# Загрузка данных о фильмах из нового файла CSV
movies = pd.read_csv('MovieData.csv')

# Преобразование рейтингов в числовой тип
movies['ratingKP'] = pd.to_numeric(movies['ratingKP'],
                                   errors='coerce').fillna(0)
movies['ratingImdb'] = pd.to_numeric(movies['ratingImdb'],
                                     errors='coerce').fillna(0)
movies['Year'] = pd.to_numeric(movies['Year'],
                               errors='coerce').fillna(0).astype(int)

# old API 7008011432:AAGzB8Njxp2C8LwxjOCMEh2PomlK-DHIyp4
bot = telebot.TeleBot('7606959553:AAGS4AwiHLHoafx_vuKOxB4mPW1SPSLSTKY')

keep_alive()


@bot.message_handler(commands=['start'])
def start(message):
    show_main_menu(message)


def show_main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Искать фильм 🍿')
    button2 = types.KeyboardButton('Топ фильмов по жанру 🎥')
    button3 = types.KeyboardButton('Топ фильмы за год 🔥')
    button4 = types.KeyboardButton('Топ фильмы режиссера 🎬')
    button5 = types.KeyboardButton('Топ фильмы актёра 🌟')
    markup.row(button1)
    markup.row(button2, button3)
    markup.row(button4, button5)
    bot.send_message(message.chat.id,
                     'Выберите действие:',
                     reply_markup=markup)
    bot.register_next_step_handler(message, on_click)


def on_click(message):
    try:
        if message.text == 'Искать фильм 🍿':
            msg = bot.send_message(message.chat.id, 'Введите название фильма:')
            bot.register_next_step_handler(msg, search_movie)
        elif message.text == 'Топ фильмов по жанру 🎥':
            genres = movies['Genres'].apply(eval).explode().unique()
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for genre in genres:
                markup.add(types.KeyboardButton(genre))
            msg = bot.send_message(message.chat.id,
                                   'Выберите жанр:',
                                   reply_markup=markup)
            bot.register_next_step_handler(msg, select_genre)
        elif message.text == 'Топ фильмы за год 🔥':
            msg = bot.send_message(message.chat.id,
                                   'Введите год выхода фильмов:')
            bot.register_next_step_handler(msg, get_year)
        elif message.text == 'Топ фильмы режиссера 🎬':
            msg = bot.send_message(message.chat.id, 'Введите имя режиссёра:')
            bot.register_next_step_handler(msg, get_director)
        elif message.text == 'Топ фильмы актёра 🌟':
            msg = bot.send_message(message.chat.id, 'Введите имя актёра:')
            bot.register_next_step_handler(msg, get_actor)
        else:
            bot.send_message(message.chat.id,
                             'Нажмите на любую из кнопок внизу экрана 👁️👄👁️')
            show_main_menu(message)
    except Exception as e:
        bot.send_message(message.chat.id, f'Произошла ошибка: {e}')
        show_main_menu(message)


def get_year(message):
    try:
        year = int(message.text)
        top_movies_by_year(message, year)
    except ValueError:
        bot.send_message(message.chat.id,
                         'Пожалуйста, введите корректный год.')
        show_main_menu(message)


def get_director(message):
    director = message.text
    top_movies_by_director(message, director)


def get_actor(message):
    actor = message.text
    top_movies_by_actor(message, actor)


def search_movie(message):
    movie_name = message.text
    found_movies = movies[movies['NameFilm'].str.contains(movie_name,
                                                          case=False,
                                                          na=False)]
    if found_movies.empty:
        msg = bot.send_message(message.chat.id,
                               'Фильм не найден. Попробуйте ещё раз:')
        bot.register_next_step_handler(msg, search_movie)
    else:
        movie = found_movies.iloc[0]
        show_movie_details(message, movie)


def select_genre(message):
    genre = message.text
    top_movies_by_genre(message, genre)


def top_movies_by_genre(message, genre):
    genre_movies = movies[movies['Genres'].str.contains(genre)]
    top_movies = genre_movies.nlargest(10, 'ratingKP')

    if top_movies.empty:
        bot.send_message(message.chat.id, 'Фильмы этого жанра не найдены.')
        show_main_menu(message)
    else:
        send_top_movies(message, top_movies, genre)


def top_movies_by_year(message, year):
    year_movies = movies[movies['Year'] == year]
    top_movies = year_movies.nlargest(10, 'ratingKP')

    if top_movies.empty:
        bot.send_message(message.chat.id, f'Фильмы за {year} год не найдены.')
        show_main_menu(message)
    else:
        send_top_movies(message, top_movies, f'{year} года')


def top_movies_by_director(message, director):
    director_movies = movies[movies['Directors'].str.contains(director,
                                                              case=False,
                                                              na=False)]
    top_movies = director_movies.nlargest(10, 'ratingKP')

    if top_movies.empty:
        bot.send_message(message.chat.id,
                         f'Фильмы режиссёра {director} не найдены.')
        show_main_menu(message)
    else:
        send_top_movies(message, top_movies, f'режиссёра {director}')


def top_movies_by_actor(message, actor):
    actor_movies = movies[movies['Actors'].str.contains(actor,
                                                        case=False,
                                                        na=False)]
    top_movies = actor_movies.nlargest(10, 'ratingKP')

    if top_movies.empty:
        bot.send_message(message.chat.id,
                         f'Фильмы с актёром {actor} не найдены.')
        show_main_menu(message)
    else:
        send_top_movies(message, top_movies, f'с актёром {actor}')


def send_top_movies(message, top_movies, category):
    try:
        movie_list = '\n'.join([
            f"{i + 1}. {row['NameFilm']} - рейтинг {row['ratingKP']}"
            for i, (_, row) in enumerate(top_movies.iterrows())
        ])
        bot.send_message(message.chat.id,
                         f"Топ фильмов по {category}:\n{movie_list}")

        markup = types.InlineKeyboardMarkup()
        for _, row in top_movies.iterrows():
            button = types.InlineKeyboardButton(
                f"{row['NameFilm']}", callback_data=f"movie_{row['KPid']}")
            markup.add(button)
        bot.send_message(message.chat.id,
                         'Выберите фильм для подробностей:',
                         reply_markup=markup)
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f'Произошла ошибка при формировании списка фильмов: {e}')
        show_main_menu(message)


def show_movie_details(message, movie):
    try:
        bot.send_message(
            message.chat.id, f"{movie['NameFilm']} ({int(movie['Year'])})\n"
            f"Описание: {movie['Description']}\n"
            f"Рейтинг Кинопоиска: {movie['ratingKP']}\n"
            f"Рейтинг IMDb: {movie['ratingImdb']}")
        bot.send_photo(message.chat.id, movie['PosterUrl'])
        markup = types.InlineKeyboardMarkup()
        watch_button = types.InlineKeyboardButton('Смотреть фильм',
                                                  url=movie['WebUrl'])
        kp_button = types.InlineKeyboardButton('Страница на Кинопоиске',
                                               url=movie['WebUrl2'])
        markup.add(watch_button)
        markup.add(kp_button)
        bot.send_message(message.chat.id,
                         'Выберите действие:',
                         reply_markup=markup)
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f'Произошла ошибка при показе информации о фильме: {e}')
    show_main_menu(message)


@bot.callback_query_handler(func=lambda call: call.data.startswith('movie_'))
def callback_movie_details(call):
    try:
        movie_id = int(call.data.split('_')[1])
        movie = movies[movies['KPid'] == movie_id].iloc[0]
        show_movie_details(call.message, movie)
    except Exception as e:
        bot.send_message(
            call.message.chat.id,
            f'Произошла ошибка при получении данных о фильме: {e}')
        show_main_menu(call.message)


# Бесконечный цикл для обработки переподключений
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Ошибка: {e}")
