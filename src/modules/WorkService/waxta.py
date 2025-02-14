import cv2
import numpy as np
import pyautogui
import time

# Загружаем единственное эталонное изображение
template = cv2.imread('../../../resources/images/ImgWaxta/ButtonE.png', 0)


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
    if find_template_on_screen(template):
        while find_template_on_screen(template):
            pyautogui.press("e")
            print("Обнаружено ButtonE.png, нажата клавиша e")
            time.sleep(1 / 32)  # Нажатие каждую секунду

    time.sleep(1)