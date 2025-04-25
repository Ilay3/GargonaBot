import os
import datetime
from pathlib import Path
from PIL import ImageGrab


def take_screenshot():
    try:
        # Определяем корневую директорию проекта
        base_dir = Path(__file__).resolve().parent.parent.parent
        save_dir = base_dir / "resources" / "screenshots"

        # Создаем директорию если не существует
        save_dir.mkdir(parents=True, exist_ok=True)

        # Генерируем имя файла
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_path = save_dir / f"screenshot_{timestamp}.png"

        # Делаем и сохраняем скриншот
        ImageGrab.grab().save(screenshot_path)
        return str(screenshot_path)

    except Exception as e:
        print(f"[ERROR] Failed to take screenshot: {str(e)}")
        return None