import cv2
import numpy as np
import pyautogui
import time
import sys
import os
import json
from datetime import datetime

def get_resource_path(relative_path):
    """Возвращает абсолютный путь к ресурсу, работает для dev и для PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        # Если запущено из .exe, используем временную папку
        base_path = sys._MEIPASS
    else:
        # Если запущено из скрипта, используем текущую директорию
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def run_autoeat(
    template_path=get_resource_path(os.path.join("resources", "images", "ImgEat", "golod.png")),
    settings_file=get_resource_path("settings.json"),
    threshold=0.7,
):
    print("Функция run_autoeat запущена.")
    """
    Запускает процесс поиска шаблона на экране:
    1. Ищет изображение шаблона (golod.png) на экране.
    2. Если шаблон найден, нажимает клавишу, указанную в настройках.
    3. Цикл повторяется бесконечно.

    :param template_path: Путь к изображению шаблона.
    :param settings_file: Путь к файлу настроек.
    :param threshold: Порог совпадения шаблона.
    """
    pyautogui.FAILSAFE = False

    

    def load_settings():
        """Загружает настройки из файла settings.json."""
        if os.path.exists(settings_file):
            try:
                with open(settings_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Ошибка загрузки настроек: {e}")
        return {}

    def find_template_on_screen(template):
        """Ищет шаблон на экране и возвращает True, если найдено совпадение."""
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        print(f"Максимальное значение совпадения: {max_val}")

        if max_val >= threshold:
            print(f"Совпадение найдено! Координаты: {max_loc}")
            return True
        return False

    # Логирование путей
    print(f"Абсолютный путь к шаблону: {template_path}")
    print(f"Абсолютный путь к файлу настроек: {settings_file}")

    # Проверка существования файлов
    if not os.path.exists(template_path):
        print(f"Ошибка: файл шаблона не найден: {template_path}")
        return
    if not os.path.exists(settings_file):
        print(f"Ошибка: файл настроек не найден: {settings_file}")
        return

    # Загрузка шаблона изображения
    template = cv2.imread(template_path, 0)
    if template is None:
        print(f"Ошибка: не удалось загрузить изображение шаблона {template_path}")
        return
    else:
        print("Шаблон успешно загружен.")

    # Загрузка настроек и получение клавиши для автоеда
    settings = load_settings()
    autoeat_key = settings.get("autoeat_key", "o")
    print(f"Запуск скрипта Autoeat с клавишей: '{autoeat_key}'")

    print("Сервис запущен...")
    while True:
        print("Поиск шаблона на экране...")
        if find_template_on_screen(template):
            print("Шаблон обнаружен. Начинаем нажатия клавиши...")
            while find_template_on_screen(template):
                pyautogui.press(autoeat_key)
                print(f"Обнаружен недостаток еды, нажата клавиша '{autoeat_key}'")
                time.sleep(10)
        else:
            print("Шаблон не обнаружен. Проверка через 15 секунд...")
        time.sleep(15)


if __name__ == "__main__":
    if "--service=autoeat" in sys.argv:
        run_autoeat()
    else:
        print("Флаг --service=autoeat не передан, выход из программы.")