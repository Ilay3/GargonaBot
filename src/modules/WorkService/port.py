import cv2
import numpy as np
import pyautogui
import time
from datetime import datetime
import keyboard
import sys


def template_matching_service(image_path):
    """Запускает сервис по поиску изображения и взаимодействию с ним."""
    pyautogui.FAILSAFE = False

    def log(message):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

    def get_pixel_color(x, y):
        return pyautogui.pixel(x, y)

    def port():
        while True:
            right = get_pixel_color(963, 495)
            left = get_pixel_color(956, 495)
            mid = get_pixel_color(959, 495)

            if right == (126, 211, 33) and left == (126, 211, 33):
                pyautogui.press('e')
            elif mid != (231, 33, 57):
                pyautogui.press('e')
            time.sleep(0.01)

    def find_template_on_screen(template, threshold=0.9):
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
        time.sleep(0.05)


if __name__ == "__main__":
    if "--service" in sys.argv:
        template_matching_service('../../../resources/images/ImgPort/ButtonE.png')
    else:
        print("Флаг --service не передан, выход из программы.")