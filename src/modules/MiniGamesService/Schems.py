import cv2
import numpy as np
import pyautogui
import time
import threading
from datetime import datetime

# Загружаем эталонные изображения в градациях серого
template_first = cv2.imread('../../../resources/images/ImgSchems/Rabota.png', 0)
template_second = cv2.imread('../../../resources/images/ImgSchems/StopButton.png', 0)

running = False  # Флаг активности schemas()
stop_event = threading.Event()  # Флаг для остановки всей программы

# Координаты области поиска второй картинки (X, Y, ширина, высота)
search_region = (583, 986, 1390, 1060)  # Установи нужные координаты


def log(message):
    """Выводит сообщение с текущим временем."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")


def get_pixel_color(x, y):
    return pyautogui.pixel(x, y)


def schemas():
    """Функция работы схем, управляется флагом running."""
    global running
    running = True
    while running and not stop_event.is_set():
        right = get_pixel_color(963, 495)
        left = get_pixel_color(956, 495)
        mid = get_pixel_color(959, 495)

        if right == (126, 211, 33) and left == (126, 211, 33):  # 0x7ed321 в RGB
            pyautogui.press('e')
        elif mid != (231, 33, 57):  # 0xe72139 в RGB
            pyautogui.press('e')

        time.sleep(0.01)  # Таймаут для снижения нагрузки на CPU


def find_template_on_screen(template, threshold=0.8, region=None):
    """
    Ищет шаблон на экране.
    region: (x, y, width, height) – ограничение области поиска.
    """
    if region:
        screenshot = pyautogui.screenshot(region=region)  # Снимок только заданной области
    else:
        screenshot = pyautogui.screenshot()  # Полный экран

    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    if len(loc[0]) > 0:
        log(f"Совпадение найдено! Координаты: {list(zip(loc[1], loc[0]))}")
        return True
    return False


def search_first():
    """Поток для поиска первой картинки (Rabota.png) на всём экране."""
    global running
    while not stop_event.is_set():
        if find_template_on_screen(template_first):  # Ищем на всём экране
            if not running:
                log("Первая картинка найдена! Запускаем schemas()...")
                running = True
                threading.Thread(target=schemas, daemon=True).start()
        time.sleep(0.1)


def search_second():
    """Поток для поиска второй картинки (StopButton.png) в заданной области."""
    global running
    while not stop_event.is_set():
        if running and find_template_on_screen(template_second, region=search_region):  # Ищем только в области
            log("Вторая картинка найдена! Останавливаем всю программу...")
            running = False  # Останавливаем schemas()
            stop_event.set()  # Останавливаем все потоки
            return  # Выход из потока

        time.sleep(0.1)


# Запуск потоков
threading.Thread(target=search_first, daemon=True).start()  # Поиск первой картинки на всём экране
threading.Thread(target=search_second, daemon=True).start()  # Поиск второй картинки в области

# Основной поток (ждёт завершения)
try:
    while not stop_event.is_set():
        time.sleep(1)
except KeyboardInterrupt:
    stop_event.set()  # Останавливаем потоки при выходе
    log("Программа завершена.")

# Координаты области поиска второй картинки (X, Y, ширина, высота)
search_region = (583, 986, 1390, 1060)  # Установи нужные координаты