import cv2
import numpy as np
import pyautogui
import time
import os


pyautogui.FAILSAFE = False

# Загружаем эталонные изображения
templates = {
    "ButtonE": cv2.imread('../../../resources/images/ImgStroyka/ButtonE.png', 0),
    "ButtonF": cv2.imread('../../../resources/images/ImgStroyka/ButtonF.png', 0),
    "ButtonY": cv2.imread('../../../resources/images/ImgStroyka/ButtonY.png', 0),
}

# Сопоставление изображений с кнопками
key_mapping = {
    "ButtonE": "e",
    "ButtonF": "f",
    "ButtonY": "y"
}


def find_template_on_screen(template, threshold=0.9):
    """Ищет шаблон на экране, возвращает True, если найдено."""
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    return len(loc[0]) > 0


# Бесконечный цикл поиска
while True:
    for key, template in templates.items():
        if find_template_on_screen(template):
            while find_template_on_screen(template):
                pyautogui.press(key_mapping[key])
                print(f"Обнаружено {key}.png, нажата клавиша {key_mapping[key]}")
                time.sleep(1/64)  # Нажатие каждую секунду

    time.sleep(1)
