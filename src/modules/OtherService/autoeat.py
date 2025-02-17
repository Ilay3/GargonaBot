import cv2
import numpy as np
import pyautogui
import time
import os
import json

pyautogui.FAILSAFE = False

# Определяем базовый каталог – где находится этот файл
current_dir = os.path.dirname(os.path.abspath(__file__))
parts = current_dir.split(os.sep)
if "src" in parts:
    src_index = parts.index("src")
    PROJECT_ROOT = os.sep.join(parts[:src_index])
else:
    PROJECT_ROOT = current_dir

# Файл настроек находится в корневой папке проекта
SETTINGS_FILE = os.path.join(PROJECT_ROOT, "settings.json")
print(f"Используется файл настроек: {SETTINGS_FILE}")


def load_settings():
    """Загружает настройки из файла settings.json."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
    return {}

# Загружаем настройки и получаем клавишу для автоеда (по умолчанию "o")
settings = load_settings()
autoeat_key = settings.get("autoeat_key", "o")
print(f"Запуск скрипта Autoeat с клавишей: '{autoeat_key}'")

# Путь к изображению шаблона
template_path = '../../../resources/images/ImgEat/golod.png'

# Загружаем эталонное изображение в оттенках серого
template = cv2.imread(template_path, 0)
if template is None:
    print(f"Ошибка: не удалось загрузить изображение шаблона по пути {template_path}")
    exit(1)

def find_template_on_screen(template, threshold=0.9):
    """Ищет шаблон на экране, возвращает True, если найдено."""
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    return len(loc[0]) > 0

print("Запуск скрипта Autoeat...")

while True:
    if find_template_on_screen(template):
        print("Шаблон обнаружен. Нажимаем клавишу для автоеда...")
        while find_template_on_screen(template):
            pyautogui.press(autoeat_key)  # Используем клавишу из настроек
            print(f"Обнаружен недостаток еды, нажата клавиша '{autoeat_key}'")
            time.sleep(10)
    else:
        print("Шаблон не обнаружен. Проверка через 15 секунд...")
    time.sleep(15)
