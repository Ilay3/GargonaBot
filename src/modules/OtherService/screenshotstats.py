import os
import datetime
import time
from pathlib import Path
from PIL import ImageGrab
import keyboard

# Указываем путь к папке для сохранения скриншотов
save_dir = Path("../../../resources/screenshots/")
save_dir.mkdir(parents=True, exist_ok=True)  # Создаем папку, если её нет

# Нажатие кнопки F10
keyboard.press_and_release('f10')

# Задержка перед созданием скриншота
time.sleep(3)

# Формируем имя файла с датой и временем
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
screenshot_path = save_dir / f"screenshot_{timestamp}.png"

# Делаем скриншот и сохраняем
screenshot = ImageGrab.grab()
screenshot.save(screenshot_path)

print(f"Скриншот сохранен: {screenshot_path}")

# Задержка перед нажатием ESC
time.sleep(3)
keyboard.press_and_release('esc')
