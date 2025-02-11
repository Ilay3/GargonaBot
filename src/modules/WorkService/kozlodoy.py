import cv2
import numpy as np
import pyautogui
import time
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Определение областей поиска (ЗАМЕНИТЕ НА ВАШИ КООРДИНАТЫ)
AREA_A = [(836, 826), (926, 826), (836, 909), (926, 909)]  # Координаты первой области
AREA_D = [(980, 826), (1075, 826), (980, 909), (1075, 909)]  # Координаты второй области
AREA_STOP = [(1203, 854), (1236, 854), (1203, 535), (1236, 535)]  # Координаты области остановки

# Определяем диапазон белого цвета (BGR)
LOWER_COLOR = np.array([0, 0, 200])  # Нижний порог белого цвета
UPPER_COLOR = np.array([180, 30, 255])  # Верхний порог белого цвета

# Определяем цвет, который при обнаружении остановит поиск (пример: красный)
STOP_LOWER_COLOR = np.array([0, 100, 100])
STOP_UPPER_COLOR = np.array([10, 255, 255])


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


while True:
    if find_color_in_area(AREA_STOP, STOP_LOWER_COLOR, STOP_UPPER_COLOR):
        logging.info("Обнаружен запрещенный цвет в области STOP! Приостанавливаем поиск на 4 секунды.")
        time.sleep(5.5)
        continue

    if find_color_in_area(AREA_A, LOWER_COLOR, UPPER_COLOR):
        logging.info("Белый цвет найден в области A, ожидание 0.50 секунды перед нажатием 'A'")
        time.sleep(1/24)
        pyautogui.press("a")
        logging.info("Нажата клавиша 'A'")
    elif find_color_in_area(AREA_D, LOWER_COLOR, UPPER_COLOR):
        logging.info("Белый цвет найден в области D, ожидание 0.50 секунды перед нажатием 'D'")
        time.sleep(1/24)
        pyautogui.press("d")
        logging.info("Нажата клавиша 'D'")

    time.sleep(0.2)  # Маленькая пауза перед следующей проверкой

