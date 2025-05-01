import cv2
import numpy as np
import pyautogui
import time
import sys
import os
from datetime import datetime

def run_kosyaki(f_button_path="../../../resources/images/ImgKosyaki/F.png", threshold=0.9):
    print("Функция run_kosyaki запущена.")
    """
    Удерживает клавишу F, пока изображение шаблона присутствует на экране.

    :param f_button_path: Путь к изображению кнопки F.
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
            log(f"Шаблон F найден! Координаты: {list(zip(loc[1], loc[0]))}")
            return True
        return False

    # Преобразование относительного пути в абсолютный
    script_dir = os.path.dirname(os.path.abspath(__file__))
    f_button_path = os.path.abspath(os.path.join(script_dir, f_button_path))

    log(f"Путь к F: {f_button_path}")

    # Загрузка шаблона изображения
    f_template = cv2.imread(f_button_path, 0)

    if f_template is None:
        log("Ошибка: не удалось загрузить изображение F.")
        return

    log("Сервис запущен...")

    # Флаг для отслеживания состояния клавиши F
    is_f_key_held = False

    while True:
        if find_template_on_screen(f_template):
            if not is_f_key_held:
                pyautogui.keyDown("f")
                is_f_key_held = True
                log("Начато удержание клавиши F.")
        else:
            if is_f_key_held:
                pyautogui.keyUp("f")
                is_f_key_held = False
                log("Клавиша F отпущена.")

        time.sleep(1)

if __name__ == "__main__":
    if "--service=kosyaki" in sys.argv:
        run_kosyaki()
    else:
        print("Флаг --service=kosyaki не передан, выход из программы.")
