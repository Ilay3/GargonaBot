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
# Путь к изображению шаблона (формируется относительно корня проекта)
template_path = '../../../resources/images/ImgMood/Mood.png'

# Загружаем эталонное изображение в градациях серого
template = cv2.imread(template_path, 0)
if template is None:
    print(f"Ошибка: не удалось загрузить изображение шаблона по пути {template_path}")
    exit(1)

def load_settings():
    """Загружает настройки из файла settings.json, расположенного в корне проекта."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
    return {}

# Загружаем настройки и получаем automood_key (по умолчанию "l")
settings = load_settings()
automood_key = settings.get("automood_key", "l")
print(f"Запуск automood скрипта с клавишей: '{automood_key}'")
print(f"Используется файл настроек: {SETTINGS_FILE}")

def find_template_on_screen(template, threshold=0.9):
    """Ищет шаблон на экране, возвращает True, если найдено."""
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    return len(loc[0]) > 0

while True:
    if find_template_on_screen(template):
        print("Шаблон обнаружен. Начинаем нажатия клавиши...")
        while find_template_on_screen(template):
            pyautogui.press(automood_key)
            print(f"Обнаружен недостаток настроения, нажата клавиша '{automood_key}'")
            time.sleep(10)
    else:
        print("Шаблон не обнаружен. Проверка через 15 секунд...")
    time.sleep(15)
