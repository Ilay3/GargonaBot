import cv2
import numpy as np
import pyautogui
import time


pyautogui.FAILSAFE = False
# Загружаем эталонные изображения
TEMPLATES = [
    cv2.imread("../../../resources/images/ImgTaxi/KPK.png", 0),  # Первая картинка
    cv2.imread("../../../resources/images/ImgTaxi/taxiAccept.png", 0), # Вторая картинка
    cv2.imread("../../../resources/images/ImgTaxi/zakazgotov.png", 0)   # Третья картинка
]

def find_template_on_screen(template, threshold=0.9):
    """Ищет шаблон на экране, возвращает координаты центра, если найдено."""
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    if len(loc[0]) > 0:
        # Находим координаты центра найденного шаблона
        max_loc = (loc[1][0], loc[0][0])
        w, h = template.shape[::-1]
        center = (max_loc[0] + w // 2, max_loc[1] + h // 2)
        return center
    return None

# Нажимаем 'm' перед первым циклом
pyautogui.press('m')
time.sleep(0.1)  # Небольшая задержка перед началом работы

while True:
    first_found = False
    second_found = False
    third_found = False

    while not third_found:
        for i, template in enumerate(TEMPLATES):
            center = find_template_on_screen(template)
            if center:
                pyautogui.click(center)
                print(f"Обнаружена картинка {i+1}, нажата мышь в {center}")
                time.sleep(0.001)  # Задержка 1 миллисекунда

                if i == 0 and not first_found:
                    first_found = True
                elif i == 1 and first_found and not second_found:
                    second_found = True
                elif i == 2 and second_found:
                    third_found = True
                    break  # Выход из цикла, чтобы начать заново

        time.sleep(0.001)  # Задержка между итерациями

    # Если третья картинка найдена, нажимаем 'm' и начинаем заново
    print("Третья картинка найдена, нажимаем 'm' и начинаем заново.")
    pyautogui.press('m')
    time.sleep(0.1)  # Небольшая задержка перед новым циклом



