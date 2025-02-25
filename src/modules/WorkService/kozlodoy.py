import cv2
import numpy as np
import pyautogui
import time
import logging
import sys
import os
from datetime import datetime

def run_kozlodoy(
    area_a_coords=[(836, 826), (926, 826), (836, 909), (926, 909)],
    area_d_coords=[(980, 826), (1075, 826), (980, 909), (1075, 909)],
    area_stop_coords=[(1203, 854), (1236, 854), (1203, 535), (1236, 535)],
    lower_color=np.array([0, 0, 200]),
    upper_color=np.array([180, 30, 255]),
    stop_lower_color=np.array([0, 100, 100]),
    stop_upper_color=np.array([10, 255, 255]),
):
    print("Функция run_color_detection запущена.")
    """
    Запускает процесс поиска цвета в указанных областях:
    1. Ищет белый цвет в областях A и D.
    2. Если белый цвет найден, нажимает соответствующую клавишу (A или D).
    3. Если обнаружен запрещенный цвет в области STOP, приостанавливает поиск.
    4. Цикл повторяется бесконечно.

    :param area_a_coords: Координаты области A.
    :param area_d_coords: Координаты области D.
    :param area_stop_coords: Координаты области STOP.
    :param lower_color: Нижний порог белого цвета.
    :param upper_color: Верхний порог белого цвета.
    :param stop_lower_color: Нижний порог запрещенного цвета.
    :param stop_upper_color: Верхний порог запрещенного цвета.
    """
    pyautogui.FAILSAFE = False

    def log(message):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

    def extract_region(image, points):
        """Обрезает изображение по заданным точкам."""
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        pts = np.array(points, dtype=np.int32)
        cv2.fillPoly(mask, [pts], 255)
        return cv2.bitwise_and(image, image, mask=mask)

    def find_color_in_area(area_points, lower_color, upper_color):
        """Ищет указанный цвет в указанной области."""
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        region = extract_region(hsv, area_points)
        mask = cv2.inRange(region, lower_color, upper_color)
        return np.any(mask > 0)

    log("Сервис запущен...")
    while True:
        if find_color_in_area(area_stop_coords, stop_lower_color, stop_upper_color):
            log("Обнаружен запрещенный цвет в области STOP! Приостанавливаем поиск на 4 секунды.")
            time.sleep(5.5)
            continue

        if find_color_in_area(area_a_coords, lower_color, upper_color):
            log("Белый цвет найден в области A, ожидание 0.50 секунды перед нажатием 'A'")
            time.sleep(1/32)
            pyautogui.press("a")
            log("Нажата клавиша 'A'")
        elif find_color_in_area(area_d_coords, lower_color, upper_color):
            log("Белый цвет найден в области D, ожидание 0.50 секунды перед нажатием 'D'")
            time.sleep(1/32)
            pyautogui.press("d")
            log("Нажата клавиша 'D'")

        time.sleep(0.4) #Маленькая пауза перед следующей проверкой


if __name__ == "__main__":
    if "--service=kozlodoy" in sys.argv:
        run_kozlodoy()
    else:
        print("Флаг --service=color_detection не передан, выход из программы.")