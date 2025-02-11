import cv2
import numpy as np
import pyautogui
import time
from datetime import datetime

# Загружаем эталонное изображение в градациях серого
template = cv2.imread('../../../resources/images/ImgPort/ButtonE.png', 0)

def log(message):
    """Выводит сообщение с текущим временем."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

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
        time.sleep(0.50)  # Ожидание 50 сотых секунды (0.66 секунды)
        pyautogui.press("e")
        log("Нажата клавиша E")

    time.sleep(0.05)  # Маленькая пауза перед следующей проверкой
