#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль для парсинга данных о фильмах с API Кинопоиска.

Этот модуль получает информацию о фильмах через Kinopoisk API Unofficial,
обрабатывает данные и сохраняет их в CSV-файл.

.. note::
    Для работы модуля требуется API-ключ от Kinopoisk API Unofficial.
    Получить ключ можно по ссылке: https://kinopoiskapiunofficial.tech/
"""

from LxmlSoup import LxmlSoup
import requests
from random import random, randint
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup

# Конфигурационные параметры
headers = {
    'X-API-KEY': 'ab6012c7-ec2d-4d19-949c-1c2d30f31d1f',  # Замените на свой API-ключ
    'Content-Type': 'application/json'
}

# Инициализация списков для хранения данных
KPid = []  # ID фильма на Кинопоиске
NameFilm = []  # Название фильма на русском
NameFilmEn = []  # Название фильма на английском
PosterUrl = []  # URL постера в полном размере
PosterUrlSmall = []  # URL постера в уменьшенном размере
Description = []  # Описание фильма
Countries = []  # Страны производства
ratingMpaa = []  # Возрастное ограничение (MPAA)
ratingAgeLimits = []  # Возрастное ограничение
Type = []  # Тип (фильм/сериал)
Year = []  # Год выпуска
Genres = []  # Жанры
ratingImdb = []  # Рейтинг IMDB
ratingKP = []  # Рейтинг Кинопоиска
AverageRating = []  # Средневзвешенный рейтинг
filmLength = []  # Длительность в минутах
WebUrl = []  # URL для просмотра
Genres1 = []  # Временный список для обработки жанров
WebUrl2 = []  # Альтернативный URL

# Коэффициенты для расчета средневзвешенного рейтинга
WeightKP = 0
WeightImdb = 0


def parse_film_data(start_id=298, end_id=500):
    """
    Парсит данные о фильмах в указанном диапазоне ID.

    :param start_id: Начальный ID фильма для парсинга
    :type start_id: int
    :param end_id: Конечный ID фильма для парсинга
    :type end_id: int

    :return: None
    :rtype: None

    .. note::
        Функция сохраняет данные в файл 'output.csv' после завершения парсинга.
    """
    for i in range(start_id, end_id):
        try:
            response = requests.get(
                f'https://kinopoiskapiunofficial.tech/api/v2.2/films/{i}',
                headers=headers
            )
            film_data = response.json()

            # Инициализация переменных для расчета рейтингов
            ratingKinopoiskVoteCount = 1
            ratingImdbVoteCount = 1
            ratingFilmCritics = 1
            ratingFilmCriticsVoteCount = 1

            # Обработка данных фильма
            for section, value in film_data.items():
                if section == "kinopoiskId":
                    KPid.append(value)
                elif section == "nameRu":
                    NameFilm.append(value)
                elif section == "nameEn":
                    NameFilmEn.append(value)
                elif section == "posterUrl":
                    PosterUrl.append(value)
                elif section == "posterUrlPreview":
                    PosterUrlSmall.append(value)
                elif section == "ratingKinopoisk":
                    ratingKP.append(value)
                elif section == "ratingImdb":
                    ratingImdb.append(value)
                elif section == "ratingFilmCritics":
                    ratingFilmCritics = value
                elif section == "ratingKinopoiskVoteCount":
                    ratingKinopoiskVoteCount = value
                elif section == "ratingImdbVoteCount":
                    ratingImdbVoteCount = value
                elif section == "ratingFilmCriticsVoteCount":
                    ratingFilmCriticsVoteCount = value
                elif section == "year":
                    Year.append(value)
                elif section == "filmLength":
                    filmLength.append(value)
                elif section == "description":
                    Description.append(value)
                elif section == "ratingMpaa":
                    ratingMpaa.append(value)
                elif section == "ratingAgeLimits":
                    ratingAgeLimits.append(value)
                elif section == "countries":
                    process_countries(value)
                elif section == "genres":
                    process_genres(value)
                elif section == "type":
                    Type.append(value)
                elif section == "webUrl":
                    WebUrl2.append(value)

            # Расчет средневзвешенного рейтинга
            calculate_average_rating(
                ratingImdbVoteCount,
                ratingKinopoiskVoteCount,
                ratingFilmCriticsVoteCount,
                ratingFilmCritics
            )

            WebUrl.append(f"https://w2.kpfr.wiki/film/{i}")

        except Exception as e:
            print(f"Ошибка при обработке фильма с ID {i}: {str(e)}")

    # Сохранение данных в CSV
    save_to_csv()


def process_countries(countries_data):
    """
    Обрабатывает данные о странах производства.

    :param countries_data: Сырые данные о странах из API
    :type countries_data: list[dict] or str

    :return: None
    """
    cleaned_data = (str(countries_data)
                    .replace("country", "")
                    .replace(" ", "")
                    .replace("'", "")
                    .replace("{", "")
                    .replace(":", "")
                    .replace("[", "")
                    .replace("}", "")
                    .replace("]", "")
                    .split(","))
    Countries.append(cleaned_data)


def process_genres(genres_data):
    """
    Обрабатывает данные о жанрах.

    :param genres_data: Сырые данные о жанрах из API
    :type genres_data: list[dict] or str

    :return: None
    """
    cleaned_data = (str(genres_data)
                    .replace("genre", "")
                    .replace(" ", "")
                    .replace("'", "")
                    .replace("{", "")
                    .replace(":", "")
                    .replace("[", "")
                    .replace("}", "")
                    .replace("]", "")
                    .split(","))
    Genres.append(cleaned_data)


def calculate_average_rating(imdb_votes, kp_votes, critics_votes, critics_rating):
    """
    Рассчитывает средневзвешенный рейтинг.

    :param imdb_votes: Количество голосов на IMDB
    :type imdb_votes: int
    :param kp_votes: Количество голосов на Кинопоиске
    :type kp_votes: int
    :param critics_votes: Количество голосов критиков
    :type critics_votes: int
    :param critics_rating: Рейтинг критиков
    :type critics_rating: float

    :return: None
    """
    total_votes = imdb_votes + kp_votes + critics_votes * 1000

    if len(ratingKP) > 0:
        WeightKP = total_votes / kp_votes * ratingKP[-1]
    if len(ratingImdb) > 0:
        WeightImdb = total_votes / imdb_votes * ratingImdb[-1]

    WeightCritics = total_votes / critics_votes * critics_rating
    AverageRating.append(WeightKP + WeightCritics + WeightImdb)


def save_to_csv():
    """
    Сохраняет собранные данные в CSV-файл.

    :return: None
    """
    data = {
        'KPid': KPid,
        'Type': Type,
        'NameFilm': NameFilm,
        'NameFilmEn': NameFilmEn,
        'Year': Year,
        'Countries': Countries,
        'Genres': Genres,
        'ratingKP': ratingKP,
        'ratingImdb': ratingImdb,
        'AverageRating': AverageRating,
        'ratingMpaa': ratingMpaa,
        'ratingAgeLimits': ratingAgeLimits,
        'Description': Description,
        'WebUrl': WebUrl,
        'WebUrl2': WebUrl2
    }

    df = pd.DataFrame(data)
    df.to_csv('output.csv', index=False)


if __name__ == "__main__":
    parse_film_data()
