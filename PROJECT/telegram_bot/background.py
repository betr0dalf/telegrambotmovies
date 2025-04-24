#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль для поддержания активности Telegram-бота.

Использует Flask-сервер для ответа на ping-запросы,
что предотвращает отключение бота на бесплатных хостингах.
"""

from flask import Flask
from threading import Thread

app = Flask(__name__)


@app.route('/')
def home():
    """
  Обработчик корневого маршрута.

  Returns:
      str: Сообщение о работоспособности сервиса
  """
    return "I'm alive"


def run():
    """
  Запускает Flask-сервер на порту 80.
  """
    app.run(host='0.0.0.0', port=80)


def keep_alive():
    """
  Запускает сервер в отдельном потоке.
  """
    t = Thread(target=run)
    t.start()
