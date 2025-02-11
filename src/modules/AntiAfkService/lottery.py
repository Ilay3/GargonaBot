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
    "test3": cv2.imread('', 0),
    "test4": cv2.imread('', 0),
}


def get_moscow_time():
    """Возвращает текущее московское время."""
    return datetime.now(moscow_tz)


def get_timestamp():
    """Возвращает текущую дату и время в формате YYYY-MM-DD_HH-MM-SS"""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def save_screenshot(name):
    """Сохраняет скриншот с заданным именем и временной меткой."""
    filename = f"{name}_{get_timestamp()}.png"
    filepath = os.path.join(filename)
    pyautogui.screenshot(filepath)
    print(f"Скриншот сохранён: {filepath}")


def find_template_on_screen(template, threshold=0.5):
    """Ищет шаблон на экране, возвращает координаты центра найденного объекта."""
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    if len(loc[0]) > 0:
        y, x = loc[0][0], loc[1][0]  # Берем первые найденные координаты
        return x + template.shape[1] // 2, y + template.shape[0] // 2  # Возвращаем центр объекта
    return None


def run_process():
    """Основной процесс поиска и нажатий."""

    # Нажимаем стрелку вверх
    pyautogui.press('up')
    print("Нажата стрелка вверх")

    # 1. Поиск первой картинки (test3.png)
    while True:
        time.sleep(1)
        pos1 = find_template_on_screen(templates["test3"])

        if pos1:
            x, y = pos1
            pyautogui.click(x, y)  # Кликаем по найденной области
            print(f"Клик по test3.png в координатах: {x}, {y}")

            # Делаем первый скриншот
            save_screenshot("Лотерея-Найдена")
            break
        else:
            print("Первая картинка не найдена, продолжаем поиск...")

    # 2. Поиск второй картинки (test4.png)
    while True:
        time.sleep(1)
        pos2 = find_template_on_screen(templates["test4"])

        if pos2:
            x, y = pos2
            pyautogui.click(x, y)  # Кликаем по найденной области
            print(f"Клик по test4.png в координатах: {x}, {y}")

            # Ждем 3 секунды перед скриншотом
            time.sleep(3)

            # Делаем второй скриншот
            save_screenshot("Лотерея-Выполнено")
            break
        else:
            print("Вторая картинка не найдена, продолжаем поиск...")


# Основной цикл: запуск раз в 2 часа с 12:01 до 23:59 по МСК
while True:
    now = get_moscow_time()
    hour = now.hour
    minute = now.minute

    # Проверяем, соответствует ли текущее время условиям (каждые 2 часа начиная с 12:01)
    if hour in range(12, 24, 2) and minute == 1:
        print(f"Запуск процесса в {now.strftime('%H:%M:%S')} по МСК")
        run_process()

        # Ждем 2 часа перед следующим запуском
        next_run = now + timedelta(hours=2)
        while get_moscow_time() < next_run:
            time.sleep(30)  # Проверяем каждые 30 секунд
    else:
        print(f"Ожидание... Сейчас {now.strftime('%H:%M:%S')} по МСК")
        time.sleep(30)
