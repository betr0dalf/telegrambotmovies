"""
Альтернативный парсер данных с Кинопоиска.

Содержит:
- main: основной скрипт парсера
"""

from .main import KinopoiskParser, parse_films_range

__all__ = ['KinopoiskParser', 'parse_films_range']