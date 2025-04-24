"""
Пакет PROJECT - основной пакет для Telegram бота поиска фильмов.

Содержит:
- parser: модуль парсинга данных с кинопоиска
- Petrparser: альтернативный парсер
- telegram_bot: основной модуль бота
"""

from . import parser
from . import Petrparser
from . import telegram_bot

__version__ = '1.0'
__all__ = ['parser', 'Petrparser', 'telegram_bot']