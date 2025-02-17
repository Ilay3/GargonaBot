import cv2
import numpy as np
import pyautogui
import time
from datetime import datetime
import keyboard


pyautogui.FAILSAFE = False
# Загружаем эталонное изображение в градациях серого
template = cv2.imread('../../../resources/images/ImgPort/ButtonE.png', 0)


def log(message):
    """Выводит сообщение с текущим временем."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")


def get_pixel_color(x, y):
    return pyautogui.pixel(x, y)


def port():
    while True:
        right = get_pixel_color(963, 495)
        left = get_pixel_color(956, 495)
        mid = get_pixel_color(959, 495)

        if right == (126, 211, 33) and left == (126, 211, 33):  # 0x7ed321 в RGB
            pyautogui.press('e')
        elif mid != (231, 33, 57):  # 0xe72139 в RGB
            pyautogui.press('e')

        time.sleep(0.01)  # небольшой таймаут для снижения нагрузки на CPU


def find_template_on_screen(template, threshold=0.9):
    """Ищет шаблон на экране, возвращает True, если найдено."""
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    if len(loc[0]) > 0:
        log(f"Совпадение найдено! Координаты: {list(zip(loc[1], loc[0]))}")
        return True
    else:
        return False


# Бесконечный цикл поиска
while True:
    if find_template_on_screen(template):
        log("Изображение найдено! Ожидание 0.50 секунды перед нажатием E...")
        port()  # Здесь вызываем функцию port()
        log("Нажата клавиша E")

    time.sleep(0.05)  # Маленькая пауза перед следующей проверкой
