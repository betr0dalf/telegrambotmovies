"""
Основной модуль Telegram бота.

Содержит:
- main: основной скрипт бота
- background: модуль поддержания работы
"""

from .main import MovieBot, run_bot
from .background import keep_alive

__all__ = ['MovieBot', 'run_bot', 'keep_alive']