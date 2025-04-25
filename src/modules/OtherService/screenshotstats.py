import os
import sys
import time
from datetime import datetime
from pathlib import Path
from PIL import ImageGrab
import keyboard


def resource_path(relative_path):
    """Определяем корректный путь к ресурсам для собранного приложения"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def take_screenshot():
    """Создает скриншот экрана и возвращает путь к файлу"""
    try:
        # Создаем папку для скриншотов
        screenshots_dir = resource_path(os.path.join("resources", "screenshots"))
        save_dir = Path(screenshots_dir)
        save_dir.mkdir(parents=True, exist_ok=True)

        # Эмулируем нажатие F10 для открытия статистики в игре
        keyboard.press_and_release('f10')
        time.sleep(3)  # Ждем открытия интерфейса

        # Создаем скриншот
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_path = save_dir / f"screenshot_{timestamp}.png"

        ImageGrab.grab().save(screenshot_path)
        print(f"Скриншот создан: {screenshot_path}")

        # Закрываем интерфейс статистики
        keyboard.press_and_release('esc')
        time.sleep(1)

        return str(screenshot_path)

    except Exception as e:
        print(f"Ошибка при создании скриншота: {str(e)}")
        raise