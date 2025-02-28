import cv2
import numpy as np
import pyautogui
import time
import sys
import os
import json
from datetime import datetime

def run_autoeat(
    template_path="../../../resources/images/ImgEat/golod.png",
    settings_file="settings.json",
    threshold=0.9,
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

    def log(message):
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
        loc = np.where(res >= threshold)

        if len(loc[0]) > 0:
            log(f"Совпадение найдено! Координаты: {list(zip(loc[1], loc[0]))}")
            return True
        return False

    # Преобразование относительных путей в абсолютные
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Директория скрипта
    template_path = os.path.abspath(os.path.join(script_dir, template_path))
    settings_file = os.path.abspath(os.path.join(script_dir, settings_file))

    # Логирование путей
    log(f"Путь к шаблону: {template_path}")
    log(f"Путь к файлу настроек: {settings_file}")

    # Загрузка шаблона изображения
    template = cv2.imread(template_path, 0)
    if template is None:
        log(f"Ошибка: не удалось загрузить изображение шаблона {template_path}")
        return
    else:
        log("Шаблон успешно загружен.")

    # Загрузка настроек и получение клавиши для автоеда
    settings = load_settings()
    autoeat_key = settings.get("autoeat_key", "o")
    log(f"Запуск скрипта Autoeat с клавишей: '{autoeat_key}'")

    log("Сервис запущен...")
    while True:
        # Поиск шаблона на экране
        if find_template_on_screen(template):
            log("Шаблон обнаружен. Начинаем нажатия клавиши...")
            while find_template_on_screen(template):
                pyautogui.press(autoeat_key)  # Используем клавишу из настроек
                log(f"Обнаружен недостаток еды, нажата клавиша '{autoeat_key}'")
                time.sleep(10)  # Задержка между нажатиями
        else:
            log("Шаблон не обнаружен. Проверка через 15 секунд...")
        time.sleep(15)  # Задержка между проверками


if __name__ == "__main__":
    if "--service=autoeat" in sys.argv:
        run_autoeat()
    else:
        print("Флаг --service=autoeat не передан, выход из программы.")