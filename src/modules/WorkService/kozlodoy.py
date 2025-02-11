import cv2
import numpy as np
import pyautogui
import time
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Загружаем эталонные изображения
templates = {
    "ButtonA": cv2.imread('../../../resources/images/ImgKozlodoy/ButtonA.png', 0),
    "ButtonD": cv2.imread('../../../resources/images/ImgKozlodoy/ButtonD.png', 0),
}


def find_template_on_screen(template, threshold=0.7):
    """Ищет шаблон на экране, возвращает координаты центра найденного объекта."""
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    if len(loc[0]) > 0:
        y, x = loc[0][0], loc[1][0]
        return x + template.shape[1] // 2, y + template.shape[0] // 2
    return None


while True:
    time.sleep(1)

    pos1 = find_template_on_screen(templates["ButtonA"])
    if pos1:
        logging.info("Изображение ButtonA найдено, нажимаем 'A'")
        pyautogui.press('a')
        time.sleep(1/32)

    pos2 = find_template_on_screen(templates["ButtonD"])
    if pos2:
        logging.info("Изображение ButtonD найдено, нажимаем 'D'")
        pyautogui.press('d')
        time.sleep(1/32)

    logging.info("Изображения не найдены, продолжаем поиск...")
