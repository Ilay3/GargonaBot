import cv2
import numpy as np
import pyautogui
import time
import os
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    filename='../../../logs/koleso.txt',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logging.info("Запуск скрипта koleso.")

# Загружаем эталонные изображения
templates = {
    "DostupKoleso": cv2.imread('../../../resources/images/ImgKoleso/HomeTest.png', 0),
    "IconCasino": cv2.imread('../../../resources/images/ImgKoleso/IconCasino.png', 0),
    "InterfaceKolesa": cv2.imread('../../../resources/images/ImgKoleso/InterfaceKolesa.png', 0),
    "ButtonKoloso": cv2.imread('../../../resources/images/ImgKoleso/ButtonKoloso.png', 0)
}
logging.info("Эталонные изображения загружены.")


def get_timestamp():
    """Возвращает текущую дату и время в формате YYYY-MM-DD_HH-MM-SS"""
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logging.debug(f"Получен временной штамп: {ts}")
    return ts


def find_template_on_screen(template, threshold=0.9):
    """Ищет шаблон на экране, возвращает координаты центра найденного объекта."""
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    if len(loc[0]) > 0:
        y, x = loc[0][0], loc[1][0]  # Берем первые найденные координаты
        center = (x + template.shape[1] // 2, y + template.shape[0] // 2)
        logging.debug(f"Найден шаблон с координатами: {center}")
        return center  # Возвращаем центр объекта
    logging.debug("Шаблон не найден.")
    return None


# 1. Поиск первой картинки (DostupKoleso)
while True:
    time.sleep(1)
    pos1 = find_template_on_screen(templates["DostupKoleso"])

    if pos1:
        logging.info("Найден DostupKoleso.")

        # Нажимаем стрелку вверх
        pyautogui.press('up')
        logging.info("Нажата стрелка вверх")
        print("Нажата стрелка вверх")
        break
    else:
        logging.debug("DostupKoleso не найден, продолжаем поиск...")
        print("Первая картинка не найдена, продолжаем поиск...")

# 2-4. Последовательный поиск и клик по IconCasino, InterfaceKolesa, ButtonKoloso
for step in ["IconCasino", "InterfaceKolesa", "ButtonKoloso"]:
    while True:
        time.sleep(1)
        pos = find_template_on_screen(templates[step])

        if pos:
            x, y = pos
            pyautogui.moveTo(x, y, duration=0.2)  # Двигаем мышь к найденной области
            pyautogui.click(x, y)  # Кликаем по найденной области
            logging.info(f"Клик по {step} в координатах: {x}, {y}")
            print(f"Клик по {step}.png в координатах: {x}, {y}")
            break
        else:
            logging.debug(f"{step} не найден, продолжаем поиск...")
            print(f"{step}.png не найден, продолжаем поиск...")

# 5. Ожидание 20 секунд, клик по последнему шаблону и финальный скриншот
time.sleep(5)  # Небольшая задержка перед кликом по последнему элементу
pos_last = find_template_on_screen(templates["ButtonKoloso"])

if pos_last:
    x, y = pos_last
    pyautogui.moveTo(x, y, duration=0.2)  # Двигаем мышь к центру ButtonKoloso
    pyautogui.click(x, y)  # Клик по центру ButtonKoloso
    logging.info(f"Клик по ButtonKoloso в координатах: {x}, {y}")
    print(f"Клик по ButtonKoloso в координатах: {x}, {y}")

# Ждем 20 секунд перед финальным скриншотом
time.sleep(20)

# Делаем финальный скриншот
timestamp = get_timestamp()
screenshot_path = f"../../../screenshots/{timestamp}_final_screenshot.png"
pyautogui.screenshot(screenshot_path)
logging.info(f"Финальный скриншот сохранён по пути: {screenshot_path}")

# Нажимаем дважды ESC и BACKSPACE
pyautogui.press('esc')
logging.info("Нажата клавиша ESC.")
time.sleep(0.5)
pyautogui.press('esc')
logging.info("Нажата клавиша ESC ещё раз.")
time.sleep(0.5)
pyautogui.press('backspace')
logging.info("Нажата клавиша BACKSPACE.")
