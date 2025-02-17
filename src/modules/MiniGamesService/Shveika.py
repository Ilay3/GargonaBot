import cv2
import numpy as np
import pyautogui
import time

pyautogui.FAILSAFE = False

# Загружаем эталонные изображения
templates = {
    "ButtonW": cv2.imread('../../../resources/images/ImgShveika/ButtonW.png', 0),
    "ButtonA": cv2.imread('../../../resources/images/ImgShveika/ButtonA.png', 0),
    "ButtonS": cv2.imread('../../../resources/images/ImgShveika/ButtonS.png', 0),
    "ButtonD": cv2.imread('../../../resources/images/ImgShveika/ButtonD.png', 0),
    "StartWork": cv2.imread('../../../resources/images/ImgShveika/StartWork.png', 0),
    "StopWork": cv2.imread('../../../resources/images/ImgShveika/StopWork.png', 0),
}

# Сопоставление изображений с кнопками
key_mapping = {
    "ButtonW": "w",
    "ButtonA": "a",
    "ButtonS": "s",
    "ButtonD": "d"
}


def find_template_on_screen(template, threshold=0.9):
    """Ищет шаблон на экране, возвращает True, если найдено."""
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    return len(loc[0]) > 0


not_found_time = time.time()

while True:
    found_letter = False

    # Проверка нажатия букв W, A, S, D
    for key in ["ButtonW", "ButtonA", "ButtonS", "ButtonD"]:
        if find_template_on_screen(templates[key]):
            pyautogui.press(key_mapping[key])
            print(f"Обнаружено {key}.png, нажата клавиша {key_mapping[key]}")
            found_letter = True
            not_found_time = time.time()

    # Если буквы W, A, S, D не обнаружены в течение 3 секунд, проверяем старт работы
    if not found_letter and time.time() - not_found_time >= 3:
        if find_template_on_screen(templates["StartWork"]):
            pyautogui.press("e")
            print("Начало работы: нажата клавиша E")
            not_found_time = time.time()

    # Проверка на остановку
    if find_template_on_screen(templates["StopWork"]):
        print("Насяльника, я усталь!")
        break

    time.sleep(0.001)  # Проверка каждую миллисекунду
