import cv2
import numpy as np
import pyautogui
import time

pyautogui.FAILSAFE = False

# Загружаем эталонное изображение кнопки F
F_TEMPLATE = cv2.imread("../../../resources/images/ImgKosyaki/F.png", 0)

def find_template_on_screen(template, threshold=0.9):
    """Ищет шаблон на экране, возвращает True, если найдено."""
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    return len(loc[0]) > 0


# Флаг для отслеживания состояния клавиши F
is_f_key_held = False

while True:
    # Ищем кнопку F
    if find_template_on_screen(F_TEMPLATE):
        if not is_f_key_held:
            pyautogui.keyDown("f")  # Удерживаем клавишу F
            is_f_key_held = True
            print("Кнопка F найдена, удерживаю F.")
    else:
        if is_f_key_held:
            pyautogui.keyUp("f")  # Отпускаем клавишу F
            is_f_key_held = False
            print("Кнопка F потеряна, отпускаю F.")

    time.sleep(1)
