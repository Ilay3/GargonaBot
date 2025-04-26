import cv2
import numpy as np
import pyautogui
import time
import sys
import os
from datetime import datetime
import platform


def run_waxta(
        image_path=None,
        key_to_press='e',
        threshold=0.9,
        check_interval=1/32
):
    """
    Улучшенный сервис поиска шаблона на экране с обработкой ошибок.
    """

    # Проверка ОС
    if platform.system() != "Windows":
        return

    # Инициализация параметров
    pyautogui.FAILSAFE = False

    # Загрузка изображения шаблона
    if image_path is None:
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        image_path = os.path.join(
            base_dir, "resources", "images", "ImgWaxta", "ButtonE.png"
        )

    image_path = os.path.abspath(image_path)
    if not os.path.exists(image_path):
        return

    try:
        template = cv2.imread(image_path, 0)
        if template is None:
            raise ValueError("Не удалось загрузить изображение")
    except Exception:
        return

    def find_template_on_screen():
        """Поиск шаблона на экране с обработкой ошибок."""
        try:
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
            return np.any(res >= threshold)
        except Exception:
            return False

    try:
        while True:
            try:
                if find_template_on_screen():
                    while find_template_on_screen():
                        pyautogui.press(key_to_press)
                        time.sleep(check_interval)
                time.sleep(1)
            except KeyboardInterrupt:
                break
            except Exception:
                time.sleep(5)
    finally:
        pass


if __name__ == "__main__":
    if "--service" in sys.argv:
        run_waxta()
    else:
        print("Флаг --service не передан, выход из программы.")