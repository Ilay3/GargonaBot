import cv2
import numpy as np
import pyautogui
import time
import sys
import os
from datetime import datetime


def run_port(image_path="../../../resources/images/ImgPort/ButtonE.png", threshold=0.9, check_interval=0.01):
    """
    Запускает сервисный процесс поиска шаблона на экране и нажатия клавиши 'E' при обнаружении.

    :param image_path: Путь к эталонному изображению.
    :param threshold: Порог совпадения шаблона.
    :param check_interval: Интервал проверки экрана.
    """
    pyautogui.FAILSAFE = False

    def log(message):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

    def get_pixel_color(x, y):
        """Получает цвет пикселя по указанным координатам."""
        return pyautogui.pixel(x, y)

    def port():
        """Проверяет пиксели и нажимает 'E' при соответствии условиям."""
        while True:
            right = get_pixel_color(963, 495)
            left = get_pixel_color(956, 495)
            mid = get_pixel_color(959, 495)

            if right == (126, 211, 33) and left == (126, 211, 33):
                pyautogui.press('e')
            elif mid != (231, 33, 57):
                pyautogui.press('e')

            time.sleep(0.01)

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

    template = cv2.imread(image_path, 0)
    if template is None:
        log(f"Ошибка: не удалось загрузить изображение {image_path}")
        return

    log("Сервис запущен...")
    while True:
        if find_template_on_screen(template):
            log("Изображение найдено! Ожидание 0.50 секунды перед нажатием E...")
            port()
            log("Нажата клавиша E")
        time.sleep(check_interval)


if __name__ == "__main__":
    if "--service" in sys.argv:
        run_port()
    else:
        print("Флаг --service не передан, выход из программы.")
