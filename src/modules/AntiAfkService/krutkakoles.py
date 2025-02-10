import cv2
import numpy as np
import pyautogui
import time
import os
from datetime import datetime

# Создаем директорию для скриншотов, если её нет
screenshot_dir = os.path.join(os.getcwd(), '../../resources/screenshots')
os.makedirs(screenshot_dir, exist_ok=True)

# Загружаем эталонные изображения
templates = {
    "DostupKoleso": cv2.imread('../../../resources/images/ImgKoleso/DostupKoleso.png', 0),
    "IconCasino": cv2.imread('../../../resources/images/ImgKoleso/IconCasino.png', 0),
    "InterfaceKolesa": cv2.imread('../../../resources/images/ImgKoleso/InterfaceKolesa.png', 0),
    "ButtonKoloso": cv2.imread('../../../resources/images/ImgKoleso/ButtonKoloso.png', 0)
}


def get_timestamp():
    """Возвращает текущую дату и время в формате YYYY-MM-DD_HH-MM-SS"""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def save_screenshot(name):
    """Сохраняет скриншот с заданным именем и временной меткой."""
    filename = f"{name}_{get_timestamp()}.png"
    filepath = os.path.join(screenshot_dir, filename)
    pyautogui.screenshot(filepath)
    print(f"Скриншот сохранён: {filepath}")


def find_template_on_screen(template, threshold=0.9):
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


# 1. Поиск первой картинки (test3.png)
while True:
    time.sleep(1)
    pos1 = find_template_on_screen(templates["DostupKoleso"])

    if pos1:
        # Делаем первый скриншот (до нажатия)
        save_screenshot("Koleso_Gotovo")

        # Нажимаем стрелку вверх
        pyautogui.press('up')
        print("Нажата стрелка вверх")
        break
    else:
        print("Первая картинка не найдена, продолжаем поиск...")

# 2-4. Последовательный поиск и клик по IconCasino, InterfaceKolesa, ButtonKoloso
for step in ["IconCasino", "InterfaceKolesa", "ButtonKoloso"]:
    while True:
        time.sleep(1)
        pos = find_template_on_screen(templates[step])

        if pos:
            x, y = pos
            pyautogui.click(x, y)  # Кликаем по найденной области
            print(f"Клик по {step}.png в координатах: {x}, {y}")
            break
        else:
            print(f"{step}.png не найден, продолжаем поиск...")

# 5. Ожидание 20 секунд и финальный скриншот
time.sleep(20)
save_screenshot("Koleso_Prokrucheno")

