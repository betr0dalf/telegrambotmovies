#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Основной модуль Telegram-бота для просмотра фильмов и сериалов.

Бот предоставляет следующие функции:
- Поиск фильмов по названию
- Топ фильмов по жанру
- Топ фильмов за год
- Топ фильмов режиссера
- Топ фильмов актера
- Подробная информация о фильме

Для работы требуется:
- API-токен Telegram бота
- Файл с данными о фильмах (MovieData.csv)
- Модуль background для поддержания работы бота
"""

import telebot
from telebot import types
import pandas as pd
from background import keep_alive
import random
#  from telegram_bot.background import keep_alive


class MovieBot:
    """
    Класс для управления Telegram-ботом поиска фильмов.

    Attributes:
        bot (telebot.TeleBot): Экземпляр Telegram бота
        movies (pd.DataFrame): Данные о фильмах
    """

    def __init__(self, token: str, data_file: str = 'MovieData.csv'):
        """
        Инициализация бота.

        :param token: API-токен Telegram бота
        :type token: str
        :param data_file: Путь к файлу с данными о фильмах
        :type data_file: str
        """
        self.bot = telebot.TeleBot(token)
        self.load_movie_data(data_file)
        self.setup_handlers()

    def load_movie_data(self, data_file: str):
        """
        Загружает и обрабатывает данные о фильмах.

        :param data_file: Путь к CSV файлу с данными
        :type data_file: str
        """
        self.movies = pd.read_csv(data_file)
        # Обработка данных
        self.movies['ratingKP'] = pd.to_numeric(
            self.movies['ratingKP'], errors='coerce').fillna(0)
        self.movies['ratingImdb'] = pd.to_numeric(
            self.movies['ratingImdb'], errors='coerce').fillna(0)
        self.movies['Year'] = pd.to_numeric(
            self.movies['Year'], errors='coerce').fillna(0).astype(int)

    def setup_handlers(self):
        """Настройка обработчиков команд бота."""

        @self.bot.message_handler(commands=['start'])
        def start(message):
            self.show_main_menu(message)

        @self.bot.message_handler(func=lambda message: True)
        def handle_all_messages(message):
            self.on_click(message)

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('movie_'))
        def callback_movie_details(call):
            self.handle_movie_callback(call)

    def send_random_movie(self, message):
        """
        Отправляет пользователю случайный фильм из базы данных.

        :param message: Объект сообщения Telegram
        :type message: telebot.types.Message
        """
        movie = self.movies.sample(1).iloc[0]
        self.show_movie_details(message, movie)

    def recommend_by_genre(self, message):
        """
        Рекомендует случайный фильм по выбранному жанру.

        :param message: Объект сообщения с выбранным жанром
        :type message: telebot.types.Message

        Проверяет, что жанр существует в базе данных, затем выбирает случайный фильм
        этого жанра и показывает его детали. Если жанр не найден или фильмы отсутствуют,
        отправляет соответствующее сообщение пользователю.
        """
        genre = message.text
        if genre not in self.movies['Genres'].apply(eval).explode().unique():
            self.bot.send_message(message.chat.id,
                                  'Пожалуйста, выберите жанр из предложенных.')
            self.show_main_menu(message)
        else:
            genre_movies = self.movies[self.movies['Genres'].apply(lambda x: genre in eval(x))]
            if genre_movies.empty:
                self.bot.send_message(message.chat.id, 'Фильмы этого жанра не найдены.')
            else:
                movie = genre_movies.sample(1).iloc[0]
                self.show_movie_details(message, movie)

    def show_main_menu(self, message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton('Искать фильм 🍿')
        button2 = types.KeyboardButton('Топ фильмов по жанру 🎥')
        button3 = types.KeyboardButton('Топ фильмы за год 🔥')
        button4 = types.KeyboardButton('Топ фильмы режиссера 🎬')
        button5 = types.KeyboardButton('Топ фильмы актёра 🌟')
        button6 = types.KeyboardButton('Случайный фильм 🎲')
        button7 = types.KeyboardButton('Рекомендация по жанру 💡')

        markup.row(button1)
        markup.row(button2, button3)
        markup.row(button4, button5)
        markup.row(button6, button7)

        self.bot.send_message(message.chat.id,
                              'Выберите действие:',
                              reply_markup=markup)

    def on_click(self, message):
        """
        Обрабатывает выбор действия из главного меню.

        :param message: Объект сообщения Telegram
        :type message: telebot.types.Message
        """
        try:
            if message.text == 'Искать фильм 🍿':
                msg = self.bot.send_message(message.chat.id, 'Введите название фильма:')
                self.bot.register_next_step_handler(msg, self.search_movie)
            elif message.text == 'Топ фильмов по жанру 🎥':
                genres = self.movies['Genres'].apply(eval).explode().unique()
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                for genre in genres:
                    markup.add(types.KeyboardButton(genre))
                msg = self.bot.send_message(message.chat.id,
                                            'Выберите жанр:',
                                            reply_markup=markup)
                self.bot.register_next_step_handler(msg, self.select_genre)
            elif message.text == 'Топ фильмы за год 🔥':
                msg = self.bot.send_message(message.chat.id,
                                            'Введите год выхода фильмов:')
                self.bot.register_next_step_handler(msg, self.get_year)
            elif message.text == 'Топ фильмы режиссера 🎬':
                msg = self.bot.send_message(message.chat.id, 'Введите имя режиссёра:')
                self.bot.register_next_step_handler(msg, self.get_director)
            elif message.text == 'Топ фильмы актёра 🌟':
                msg = self.bot.send_message(message.chat.id, 'Введите имя актёра:')
                self.bot.register_next_step_handler(msg, self.get_actor)
            elif message.text == 'Случайный фильм 🎲':
                self.send_random_movie(message)
            elif message.text == 'Рекомендация по жанру 💡':
                genres = self.movies['Genres'].apply(eval).explode().unique()
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                for genre in genres:
                    markup.add(types.KeyboardButton(genre))
                msg = self.bot.send_message(message.chat.id,
                                            'Выберите жанр для рекомендации:',
                                            reply_markup=markup)
                self.bot.register_next_step_handler(msg, self.recommend_by_genre)
            else:
                self.bot.send_message(message.chat.id,
                                      'Нажмите на любую из кнопок внизу экрана 👁️👄👁️')
                self.show_main_menu(message)
        except Exception as e:
            self.bot.send_message(message.chat.id, f'Произошла ошибка: {e}')
            self.show_main_menu(message)

    def get_year(self, message):
        """
        Обрабатывает ввод года пользователем и показывает топ фильмов за этот год.

        :param message: Объект сообщения с введенным годом
        :type message: telebot.types.Message
        """
        try:
            year = int(message.text)
            self.top_movies_by_year(message, year)
        except ValueError:
            self.bot.send_message(message.chat.id,
                                  'Пожалуйста, введите корректный год (например: 2020).')
            self.show_main_menu(message)

    def get_director(self, message):
        """
        Обрабатывает ввод имени режиссера и показывает топ его фильмов.

        :param message: Объект сообщения с именем режиссера
        :type message: telebot.types.Message
        """
        director = message.text
        if len(director) < 2:
            self.bot.send_message(message.chat.id,
                                  'Имя режиссера должно содержать минимум 2 символа.')
            self.show_main_menu(message)
        else:
            self.top_movies_by_director(message, director)

    def get_actor(self, message):
        """
        Обрабатывает ввод имени актера и показывает топ фильмов с его участием.

        :param message: Объект сообщения с именем актера
        :type message: telebot.types.Message
        """
        actor = message.text
        if len(actor) < 2:
            self.bot.send_message(message.chat.id,
                                  'Имя актера должно содержать минимум 2 символа.')
            self.show_main_menu(message)
        else:
            self.top_movies_by_actor(message, actor)

    def search_movie(self, message):
        """
        Обрабатывает поиск фильма по названию.

        :param message: Объект сообщения с названием фильма
        :type message: telebot.types.Message
        """
        movie_name = message.text.strip()
        if len(movie_name) < 2:
            self.bot.send_message(message.chat.id,
                                  'Название фильма должно содержать минимум 2 символа.')
            self.show_main_menu(message)
            return

        found_movies = self.movies[
            self.movies['NameFilm'].str.contains(movie_name, case=False, na=False)
        ]

        if found_movies.empty:
            msg = self.bot.send_message(message.chat.id,
                                        'Фильм не найден. Попробуйте ещё раз:')
            self.bot.register_next_step_handler(msg, self.search_movie)
        else:
            movie = found_movies.iloc[0]
            self.show_movie_details(message, movie)

    def select_genre(self, message):
        """
        Обрабатывает выбор жанра пользователем.

        :param message: Объект сообщения с выбранным жанром
        :type message: telebot.types.Message
        """
        genre = message.text
        if genre not in self.movies['Genres'].apply(eval).explode().unique():
            self.bot.send_message(message.chat.id,
                                  'Пожалуйста, выберите жанр из предложенных.')
            self.show_main_menu(message)
        else:
            self.top_movies_by_genre(message, genre)

    def top_movies_by_genre(self, message, genre):
        """
        Показывает топ 10 фильмов по выбранному жанру.

        :param message: Объект исходного сообщения
        :type message: telebot.types.Message
        :param genre: Выбранный жанр
        :type genre: str
        """
        try:
            genre_movies = self.movies[
                self.movies['Genres'].apply(lambda x: genre in eval(x))
            ]
            top_movies = genre_movies.nlargest(10, 'ratingKP')

            if top_movies.empty:
                self.bot.send_message(message.chat.id,
                                      f'Фильмы жанра "{genre}" не найдены.')
            else:
                self.send_top_movies(message, top_movies, f'жанру "{genre}"')

            self.show_main_menu(message)
        except Exception as e:
            self.bot.send_message(message.chat.id,
                                  f'Произошла ошибка при поиске по жанру: {e}')
            self.show_main_menu(message)

    def top_movies_by_year(self, message, year):
        """
        Показывает топ 10 фильмов за указанный год.

        :param message: Объект исходного сообщения
        :type message: telebot.types.Message
        :param year: Год выпуска фильмов
        :type year: int
        """
        try:
            current_year = pd.Timestamp.now().year
            if year < 1900 or year > current_year:
                self.bot.send_message(message.chat.id,
                                      f'Пожалуйста, введите год между 1900 и {current_year}.')
                self.show_main_menu(message)
                return

            year_movies = self.movies[self.movies['Year'] == year]
            top_movies = year_movies.nlargest(10, 'ratingKP')

            if top_movies.empty:
                self.bot.send_message(message.chat.id,
                                      f'Фильмы за {year} год не найдены.')
            else:
                self.send_top_movies(message, top_movies, f'{year} году')

            self.show_main_menu(message)
        except Exception as e:
            self.bot.send_message(message.chat.id,
                                  f'Произошла ошибка при поиске по году: {e}')
            self.show_main_menu(message)

    def top_movies_by_director(self, message, director):
        """
        Показывает топ 10 фильмов указанного режиссера.

        :param message: Объект исходного сообщения
        :type message: telebot.types.Message
        :param director: Имя режиссера
        :type director: str
        """
        try:
            director_movies = self.movies[
                self.movies['Directors'].str.contains(director, case=False, na=False)
            ]
            top_movies = director_movies.nlargest(10, 'ratingKP')

            if top_movies.empty:
                self.bot.send_message(message.chat.id,
                                      f'Фильмы режиссера {director} не найдены.')
            else:
                self.send_top_movies(message, top_movies, f'режиссеру {director}')

            self.show_main_menu(message)
        except Exception as e:
            self.bot.send_message(message.chat.id,
                                  f'Произошла ошибка при поиске по режиссеру: {e}')
            self.show_main_menu(message)

    def top_movies_by_actor(self, message, actor):
        """
        Показывает топ 10 фильмов с указанным актером.

        :param message: Объект исходного сообщения
        :type message: telebot.types.Message
        :param actor: Имя актера
        :type actor: str
        """
        try:
            actor_movies = self.movies[
                self.movies['Actors'].str.contains(actor, case=False, na=False)
            ]
            top_movies = actor_movies.nlargest(10, 'ratingKP')

            if top_movies.empty:
                self.bot.send_message(message.chat.id,
                                      f'Фильмы с актером {actor} не найдены.')
            else:
                self.send_top_movies(message, top_movies, f'актеру {actor}')

            self.show_main_menu(message)
        except Exception as e:
            self.bot.send_message(message.chat.id,
                                  f'Произошла ошибка при поиске по актеру: {e}')
            self.show_main_menu(message)

    def send_top_movies(self, message, top_movies, category):
        """
        Отправляет пользователю список топ фильмов с интерактивными кнопками.

        :param message: Объект исходного сообщения
        :type message: telebot.types.Message
        :param top_movies: DataFrame с фильмами
        :type top_movies: pd.DataFrame
        :param category: Категория поиска (для заголовка)
        :type category: str
        """
        try:
            # Формируем текст сообщения
            movie_list = '\n'.join([
                f"{i + 1}. {row['NameFilm']} ({int(row['Year'])}), ★ {row['ratingKP']:.1f}"
                for i, (_, row) in enumerate(top_movies.iterrows())
            ])

            # Отправляем сообщение со списком
            self.bot.send_message(
                message.chat.id,
                f"🏆 Топ фильмов по {category}:\n\n{movie_list}",
                parse_mode='Markdown'
            )

            # Создаем интерактивные кнопки
            markup = types.InlineKeyboardMarkup()
            for _, row in top_movies.iterrows():
                btn_text = f"{row['NameFilm']} ({int(row['Year'])})"
                markup.add(types.InlineKeyboardButton(
                    btn_text,
                    callback_data=f"movie_{row['KPid']}"
                ))

            # Отправляем кнопки
            self.bot.send_message(
                message.chat.id,
                "Выберите фильм для подробной информации:",
                reply_markup=markup
            )

        except Exception as e:
            self.bot.send_message(
                message.chat.id,
                '⚠️ Произошла ошибка при формировании списка фильмов.'
            )
            self.show_main_menu(message)

    def show_movie_details(self, message, movie):
        """
        Отображает подробную информацию о фильме и интерактивные кнопки.

        :param message: Объект входящего сообщения от пользователя
        :type message: telebot.types.Message
        :param movie: Данные о фильме (строка DataFrame)
        :type movie: pandas.Series

        :raises KeyError: Если отсутствуют обязательные поля в данных фильма
        :raises Exception: При ошибках отправки сообщений или медиа

        .. note::
            Обязательные поля в данных фильма:
            - NameFilm: Название фильма
            - Year: Год выпуска
            - ratingKP: Рейтинг Кинопоиска
            - Description: Описание фильма
            - PosterUrl: URL постера
            - WebUrl: URL для просмотра
            - WebUrl2: URL страницы на Кинопоиске
        """

        try:
            # Формируем основное сообщение
            msg_text = f"🎬 *{movie['NameFilm']}* ({int(movie['Year'])})\n\n"
            msg_text += f"📝 *Описание:*\n{movie['Description']}\n\n"
            msg_text += f"📊 *Рейтинг КП:* {movie['ratingKP']:.1f}\n"
            msg_text += f"⭐ *IMDb:* {movie['ratingImdb']:.1f}\n"

            if pd.notna(movie.get('filmLength')):
                msg_text += f"⏳ *Длительность:* {movie['filmLength']} мин.\n"

            # Отправляем текстовую информацию
            self.bot.send_message(message.chat.id, msg_text, parse_mode='Markdown')

            # Отправка постера с обработкой ошибок
            if pd.notna(movie.get('PosterUrl')):
                try:
                    self.bot.send_photo(message.chat.id, movie['PosterUrl'])
                except Exception as e:
                    print(f"Ошибка отправки постера: {e}")
                    self.bot.send_message(message.chat.id, "🖼 Изображение недоступно")

            # Создаем кнопки действий
            markup = types.InlineKeyboardMarkup()
            if pd.notna(movie.get('WebUrl')):
                markup.add(types.InlineKeyboardButton(
                    '🎥 Смотреть онлайн',
                    url=movie['WebUrl']
                ))

            if pd.notna(movie.get('WebUrl2')):
                markup.add(types.InlineKeyboardButton(
                    '📌 КиноПоиск',
                    url=movie['WebUrl2']
                ))

            if markup.keyboard:
                self.bot.send_message(
                    message.chat.id,
                    "🔗 Ссылки:",
                    reply_markup=markup
                )

        except KeyError as e:
            error_msg = f"⚠️ Отсутствует обязательное поле: {str(e)}"
            self.bot.send_message(message.chat.id, error_msg)
            print(f"[ERROR] {error_msg}\nДоступные поля: {list(movie.keys())}")

        except Exception as e:
            self.bot.send_message(
                message.chat.id,
                "⚠️ Произошла ошибка при загрузке информации о фильме"
            )
            print(f"[ERROR] show_movie_details: {str(e)}")

        finally:
            self.show_main_menu(message)

    def handle_movie_callback(self, call):
        """
        Обрабатывает callback от интерактивных кнопок выбора фильма.

        :param call: Объект callback
        :type call: telebot.types.CallbackQuery
        """
        try:
            movie_id = int(call.data.split('_')[1])
            movie = self.movies[self.movies['KPid'] == movie_id].iloc[0]
            self.show_movie_details(call.message, movie)
        except IndexError:
            self.bot.send_message(
                call.message.chat.id,
                '⚠️ Фильм не найден в базе данных.'
            )
            self.show_main_menu(call.message)
        except Exception as e:
            self.bot.send_message(
                call.message.chat.id,
                '⚠️ Произошла ошибка при загрузке фильма.'
            )
            self.show_main_menu(call.message)


def run_bot(token: str):
    """
    Запускает бота с указанным токеном.

    :param token: API-токен Telegram бота
    :type token: str
    """
    keep_alive()  # Активируем фоновый сервис
    movie_bot = MovieBot(token)

    # Бесконечный цикл для обработки переподключений
    while True:
        try:
            movie_bot.bot.polling(none_stop=True)
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    # Токен бота
    BOT_TOKEN = 'token'
    run_bot(BOT_TOKEN)
