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

def run_automood(
    template_path=get_resource_path(os.path.join("resources", "images", "ImgMood", "Mood.png")),
    settings_file=get_resource_path("settings.json"),
    threshold=0.9,
):
    print("Функция run_automood запущена.")
    """
    Запускает процесс поиска шаблона на экране:
    1. Ищет изображение шаблона (Mood.png) на экране.
    2. Если шаблон найден, нажимает клавишу, указанную в настройках.
    3. Цикл повторяется бесконечно.

    :param template_path: Путь к изображению шаблона.
    :param settings_file: Путь к файлу настроек.
    :param threshold: Порог совпадения шаблона.
    """
    pyautogui.FAILSAFE = False

    def log(message):
        with open("automood.log", "a") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

    def load_settings():
        """Загружает настройки из файла settings.json."""
        if os.path.exists(settings_file):
            try:
                with open(settings_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                log(f"Ошибка загрузки настроек: {e}")
        return {}

    def find_template_on_screen(template):
        """Ищет шаблон на экране и возвращает True, если найдено совпадение."""
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        log(f"Максимальное значение совпадения: {max_val}")

        if max_val >= threshold:
            log(f"Совпадение найдено! Координаты: {max_loc}")
            return True
        return False

    # Логирование путей
    log(f"Абсолютный путь к шаблону: {template_path}")
    log(f"Абсолютный путь к файлу настроек: {settings_file}")

    # Проверка существования файлов
    if not os.path.exists(template_path):
        log(f"Ошибка: файл шаблона не найден: {template_path}")
        return
    if not os.path.exists(settings_file):
        log(f"Ошибка: файл настроек не найден: {settings_file}")
        return

    # Загрузка шаблона изображения
    template = cv2.imread(template_path, 0)
    if template is None:
        log(f"Ошибка: не удалось загрузить изображение шаблона {template_path}")
        return
    else:
        log("Шаблон успешно загружен.")

    # Загрузка настроек и получение клавиши для automood
    settings = load_settings()
    automood_key = settings.get("automood_key", "l")
    log(f"Запуск automood скрипта с клавишей: '{automood_key}'")

    log("Сервис запущен...")
    while True:
        log("Поиск шаблона на экране...")
        if find_template_on_screen(template):
            log("Шаблон обнаружен. Начинаем нажатия клавиши...")
            while find_template_on_screen(template):
                pyautogui.press(automood_key)
                log(f"Обнаружен недостаток настроения, нажата клавиша '{automood_key}'")
                time.sleep(10)
        else:
            log("Шаблон не обнаружен. Проверка через 15 секунд...")
        time.sleep(15)


if __name__ == "__main__":
    if "--service=automood" in sys.argv:
        run_automood()
    else:
        print("Флаг --service=automood не передан, выход из программы.")