#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль Petrparser - альтернативный парсер данных с Кинопоиска.

Этот модуль предоставляет дополнительный способ получения данных о фильмах
через Kinopoisk API Unofficial. Основные отличия от основного парсера:
- Использует другой подход к обработке данных
- Сохраняет данные в том же формате для совместимости
- Имеет альтернативные методы обработки ошибок

.. note::
    Требуется API-ключ от Kinopoisk API Unofficial.
    Получить ключ можно по ссылке: https://kinopoiskapiunofficial.tech/
"""

import requests
import pandas as pd
from typing import Dict, Any, List, Union

# Конфигурационные параметры API
API_HEADERS = {
    'X-API-KEY': '096e8092-9c8a-45f4-9a8f-a90339f0472d',  # Замените на свой API-ключ
    'Content-Type': 'application/json'
}

API_BASE_URL = 'https://kinopoiskapiunofficial.tech/api/v2.2/films/'


class KinopoiskParser:
    """
    Основной класс для парсинга данных с Кинопоиска.

    Attributes:
        data_containers (dict): Словарь для хранения собранных данных
        api_headers (dict): Заголовки для HTTP-запросов
    """

    def __init__(self):
        """Инициализирует контейнеры для данных и настройки API."""
        self.data_containers = {
            'KPid': [],  # ID фильма на Кинопоиске
            'NameFilm': [],  # Название на русском
            'NameFilmEn': [],  # Название на английском
            'PosterUrl': [],  # URL постера
            'PosterUrlSmall': [],  # URL уменьшенного постера
            'Description': [],  # Описание фильма
            'Countries': [],  # Страны производства
            'ratingMpaa': [],  # Рейтинг MPAA
            'ratingAgeLimits': [],  # Возрастные ограничения
            'Type': [],  # Тип (фильм/сериал)
            'Year': [],  # Год выпуска
            'Genres': [],  # Жанры
            'ratingImdb': [],  # Рейтинг IMDB
            'ratingKP': [],  # Рейтинг Кинопоиска
            'AverageRating': [],  # Средневзвешенный рейтинг
            'filmLength': [],  # Длительность
            'WebUrl': [],  # Ссылка для просмотра
            'WebUrl2': []  # Альтернативная ссылка
        }

        self.weights = {
            'kp': 0,
            'imdb': 0,
            'critics': 0
        }

    def fetch_film_data(self, film_id: int) -> Union[Dict[str, Any], None]:
        """
        Получает данные о фильме по его ID.

        :param film_id: ID фильма на Кинопоиске
        :type film_id: int
        :return: Словарь с данными фильма или None при ошибке
        :rtype: dict or None
        """
        try:
            response = requests.get(f"{API_BASE_URL}{film_id}", headers=API_HEADERS)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе данных для фильма {film_id}: {str(e)}")
            return None

    def process_film_data(self, film_data: Dict[str, Any], film_id: int):
        """
        Обрабатывает и сохраняет данные о фильме.

        :param film_data: Сырые данные о фильме от API
        :type film_data: dict
        :param film_id: ID обрабатываемого фильма
        :type film_id: int
        """
        # Инициализация значений по умолчанию
        vote_counts = {
            'kp': 1,
            'imdb': 1,
            'critics': 1
        }
        ratings = {
            'kp': None,
            'imdb': None,
            'critics': 1
        }

        # Обработка данных фильма
        for key, value in film_data.items():
            if key in self.data_containers:
                if key in ['countries', 'genres']:
                    self._process_special_field(key, value)
                else:
                    self.data_containers[key].append(value)

            # Сохраняем дополнительные данные для расчетов
            if key == 'ratingKinopoiskVoteCount':
                vote_counts['kp'] = value
            elif key == 'ratingImdbVoteCount':
                vote_counts['imdb'] = value
            elif key == 'ratingFilmCriticsVoteCount':
                vote_counts['critics'] = value
            elif key == 'ratingKinopoisk':
                ratings['kp'] = value
            elif key == 'ratingImdb':
                ratings['imdb'] = value
            elif key == 'ratingFilmCritics':
                ratings['critics'] = value

        # Расчет рейтингов
        self._calculate_ratings(vote_counts, ratings)

        # Добавление URL
        self.data_containers['WebUrl'].append(f"https://w2.kpfr.wiki/film/{film_id}")

    def _process_special_field(self, field_name: str, raw_data: Any):
        """
        Обрабатывает специальные поля (countries, genres).

        :param field_name: Название поля ('countries' или 'genres')
        :type field_name: str
        :param raw_data: Сырые данные поля
        :type raw_data: Any
        """
        cleaned_data = (str(raw_data)
                        .replace(field_name[:-1], "")  # Удаляем 'country' или 'genre'
                        .replace(" ", "")
                        .replace("'", "")
                        .replace("{", "")
                        .replace(":", "")
                        .replace("[", "")
                        .replace("}", "")
                        .replace("]", "")
                        .split(","))
        self.data_containers[field_name].append(cleaned_data)

    def _calculate_ratings(self, vote_counts: Dict[str, int], ratings: Dict[str, float]):
        """
        Рассчитывает средневзвешенный рейтинг.

        :param vote_counts: Количество голосов по источникам
        :type vote_counts: dict
        :param ratings: Рейтинги по источникам
        :type ratings: dict
        """
        total_votes = sum(vote_counts.values()) + vote_counts['critics'] * 999  # Коэф. для критиков

        if ratings['kp'] is not None:
            self.weights['kp'] = total_votes / vote_counts['kp'] * ratings['kp']
        if ratings['imdb'] is not None:
            self.weights['imdb'] = total_votes / vote_counts['imdb'] * ratings['imdb']

        self.weights['critics'] = total_votes / vote_counts['critics'] * ratings['critics']
        avg_rating = sum(self.weights.values())
        self.data_containers['AverageRating'].append(avg_rating)

    def save_to_csv(self, filename: str = 'output.csv'):
        """
        Сохраняет собранные данные в CSV файл.

        :param filename: Имя файла для сохранения
        :type filename: str
        """
        df = pd.DataFrame(self.data_containers)
        df.to_csv(filename, index=False)
        print(f"Данные успешно сохранены в {filename}")


def parse_films_range(start_id: int = 298, end_id: int = 500):
    """
    Основная функция для парсинга диапазона фильмов.

    :param start_id: Начальный ID фильма
    :type start_id: int
    :param end_id: Конечный ID фильма
    :type end_id: int
    """
    parser = KinopoiskParser()

    for film_id in range(start_id, end_id + 1):
        film_data = parser.fetch_film_data(film_id)
        if film_data:
            parser.process_film_data(film_data, film_id)

    parser.save_to_csv()


if __name__ == "__main__":
    parse_films_range()
