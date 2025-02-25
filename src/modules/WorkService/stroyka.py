import cv2
import numpy as np
import pyautogui
import time
import sys
import os
from datetime import datetime

def run_stroyka(
    button_e_path="../../../resources/images/ImgStroyka/ButtonE.png",
    button_f_path="../../../resources/images/ImgStroyka/ButtonF.png",
    button_y_path="../../../resources/images/ImgStroyka/ButtonY.png",
    threshold=0.9,
):
    print("Функция run_stroyka запущена.")
    """
    Запускает процесс поиска шаблонов на экране:
    1. Ищет изображения кнопок (ButtonE, ButtonF, ButtonY) на экране.
    2. Если изображение найдено, нажимает соответствующую клавишу (E, F, Y).
    3. Цикл повторяется бесконечно.

    :param button_e_path: Путь к изображению кнопки ButtonE.
    :param button_f_path: Путь к изображению кнопки ButtonF.
    :param button_y_path: Путь к изображению кнопки ButtonY.
    :param threshold: Порог совпадения шаблона.
    """
    pyautogui.FAILSAFE = False

    def log(message):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

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
    button_e_path = os.path.abspath(os.path.join(script_dir, button_e_path))
    button_f_path = os.path.abspath(os.path.join(script_dir, button_f_path))
    button_y_path = os.path.abspath(os.path.join(script_dir, button_y_path))

    # Логирование путей
    log(f"Путь к ButtonE: {button_e_path}")
    log(f"Путь к ButtonF: {button_f_path}")
    log(f"Путь к ButtonY: {button_y_path}")

    # Загрузка шаблонов изображений
    templates = {
        "ButtonE": cv2.imread(button_e_path, 0),
        "ButtonF": cv2.imread(button_f_path, 0),
        "ButtonY": cv2.imread(button_y_path, 0),
    }

    # Проверка загрузки изображений
    for key, template in templates.items():
        if template is None:
            log(f"Ошибка: не удалось загрузить изображение {key}")
            return

    # Сопоставление изображений с кнопками
    key_mapping = {
        "ButtonE": "e",
        "ButtonF": "f",
        "ButtonY": "y"
    }

    log("Сервис запущен...")
    while True:
        for key, template in templates.items():
            # Проверяем наличие кнопки на экране
            if find_template_on_screen(template):
                log(f"{key} найдена! Нажатие клавиши {key_mapping[key]}...")
                pyautogui.press(key_mapping[key])  # Нажатие соответствующей клавиши
                log(f"Клавиша {key_mapping[key]} нажата.")
                time.sleep(1/256)  # Задержка 1 миллисекунда

        # Минимальная задержка между итерациями цикла
        time.sleep(1/256)


if __name__ == "__main__":
    if "--service=stroyka" in sys.argv:
        run_stroyka()
    else:
        print("Флаг --service=stroyka не передан, выход из программы.")