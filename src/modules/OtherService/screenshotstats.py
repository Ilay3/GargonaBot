import sys
import os
from pathlib import Path
import datetime
import time
from PIL import ImageGrab
import keyboard

def resource_path(relative_path):
    """Возвращает абсолютный путь к файлу/ресурсу.
    При запуске в режиме onefile используется sys._MEIPASS, иначе – текущая директория."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Определяем путь к папке для скриншотов
# Предполагается, что папка resources находится в корне проекта
screenshots_dir = resource_path(os.path.join("resources", "screenshots"))
save_dir = Path(screenshots_dir)

try:
    save_dir.mkdir(parents=True, exist_ok=True)
except PermissionError as e:
    print(f"Ошибка доступа при создании папки {save_dir}: {e}")
    # Если доступ запрещён, попробуйте создать папку вручную или выберите другой путь
    exit(1)

keyboard.press_and_release('f10')
time.sleep(3)

timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
screenshot_path = save_dir / f"screenshot_{timestamp}.png"

screenshot = ImageGrab.grab()
screenshot.save(screenshot_path)

print(f"Скриншот сохранен: {screenshot_path}")
time.sleep(3)
keyboard.press_and_release('esc')