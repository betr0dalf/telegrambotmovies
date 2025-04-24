"""
Модуль парсинга данных с Кинопоиска.

Содержит:
- main: основной скрипт парсера
"""

from .main import (
    parse_film_data,
    process_countries,
    process_genres,
    calculate_average_rating,
    save_to_csv
)

__all__ = [
    'parse_film_data',
    'process_countries', 
    'process_genres',
    'calculate_average_rating',
    'save_to_csv'
]