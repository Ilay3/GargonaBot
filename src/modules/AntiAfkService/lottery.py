import cv2
import numpy as np
import pyautogui
import time
import os
from datetime import datetime, timedelta
import pytz

# Часовой пояс Москвы
moscow_tz = pytz.timezone('Europe/Moscow')

# Загружаем эталонные изображения
templates = {
    "Iconlottery": cv2.imread('../../../resources/images/ImgLottery/Iconlottery.png', 0),
    "Buttonlottery": cv2.imread('../../../resources/images/ImgLottery/Buttonlottery.png', 0),
    "Backspacetriggerlottery": cv2.imread('../../../resources/images/ImgLottery/Backspacetriggerlottery.png', 0),
}


def get_moscow_time():
    """Возвращает текущее московское время."""
    return datetime.now(moscow_tz)


def get_timestamp():
    """Возвращает текущую дату и время в формате YYYY-MM-DD_HH-MM-SS"""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def find_template_on_screen(template, threshold=0.9):
    """Ищет шаблон на экране, возвращает координаты центра найденного объекта."""
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    if len(loc[0]) > 0:
        y, x = loc[0][0], loc[1][0]  # OpenCV возвращает (y, x), но pyautogui ожидает (x, y)

        center_x = x + template.shape[1] // 2
        center_y = y + template.shape[0] // 2

        # Проверяем, не выходит ли точка за пределы экрана
        screen_width, screen_height = pyautogui.size()
        if 0 <= center_x <= screen_width and 0 <= center_y <= screen_height:
            print(f"Обнаружено изображение: ({x}, {y}), центр: ({center_x}, {center_y})")
            return center_x, center_y
        else:
            print(f"Координаты ({center_x}, {center_y}) за пределами экрана!")
            return None
    return None


def run_process():
    """Основной процесс поиска и нажатий."""
    print("Процесс запущен")
    pyautogui.press('up')
    print("Нажата стрелка вверх")

    while True:
        time.sleep(1)
        pos1 = find_template_on_screen(templates["Iconlottery"])

        if pos1:
            x, y = pos1
            pyautogui.moveTo(x, y, duration=0.2)
            pyautogui.click(x, y)
            print(f"Клик по Iconlottery в координатах: {x}, {y}")
            time.sleep(1)
            break
        else:
            print("Iconlottery не найдена, продолжаем поиск...")

    while True:
        time.sleep(1)
        pos2 = find_template_on_screen(templates["Buttonlottery"])

        if pos2:
            x, y = pos2
            pyautogui.moveTo(x, y, duration=0.2)
            pyautogui.click(x, y)
            print(f"Клик по Buttonlottery в координатах: {x}, {y}")
            time.sleep(3)
            break
        else:
            print("Buttonlottery не найдена, продолжаем поиск...")

    while True:
        time.sleep(0.05)
        backspace_pos = find_template_on_screen(templates["Backspacetriggerlottery"])
        if backspace_pos:
            pyautogui.press('backspace')
            pyautogui.press('backspace')
            print("Обнаружено второе изображение! Дважды нажат Backspace.")
            time.sleep(7200)  # Ожидание 2 часа перед следующей проверкой
            break
        else:
            print("Изображение для Backspace не найдено, продолжаем поиск...")


# Запуск кода с 12:01 до 23:59 по МСК
while True:
    now = get_moscow_time()
    if 12 <= now.hour < 24:
        print(f"Запуск процесса в {now.strftime('%H:%M:%S')} по МСК")
        run_process()
    else:
        print(f"Ожидание... Сейчас {now.strftime('%H:%M:%S')} по МСК")
        time.sleep(30)
