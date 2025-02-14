import cv2
import numpy as np
import pyautogui
import time
from datetime import datetime
import threading
import keyboard

# Загружаем эталонные изображения в градациях серого
template_first = cv2.imread('../../../resources/images/ImgSchems/Rabota.png', 0)
template_second = cv2.imread('../../../resources/images/ImgSchems/StopButton.png', 0)  # Путь ко второму изображению


def log(message):
    """Выводит сообщение с текущим временем."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")


def get_pixel_color(x, y):
    return pyautogui.pixel(x, y)


def schemas():
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


# Функция для запуска schemas() в отдельном потоке
def start_schemas():
    threading.Thread(target=schemas, daemon=True).start()


# Бесконечный цикл поиска
schemas_active = False  # Переменная для отслеживания состояния schemas()

while True:
    if find_template_on_screen(template_first):  # Если найдено первое изображение
        if not schemas_active:
            log("Первая картинка найдена! Включаем schemas()...")
            schemas_active = True
            start_schemas()  # Запуск функции schemas() в отдельном потоке
    elif find_template_on_screen(template_second):  # Если найдено второе изображение
        if schemas_active:
            log("Вторая картинка найдена! Останавливаем schemas()...")
            schemas_active = False
            break  # Останавливаем цикл, выходя из функции schemas()

    time.sleep(0.05)  # Маленькая пауза перед следующей проверкой
