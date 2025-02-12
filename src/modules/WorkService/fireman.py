import cv2
import numpy as np
import pyautogui
import time

# Загружаем эталонные изображения
first_template = cv2.imread('../../../resources/images/ImgFireman/StartButton1.png', 0)
sequence_templates = [
    cv2.imread(path, 0) for path in [
        '../../../resources/images/ImgFireman/RoadAvary.png',
        '../../../resources/images/ImgFireman/ForestAvary.png',
        '../../../resources/images/ImgFireman/Pozar2.png',
        '../../../resources/images/ImgFireman/ForestAvary.png'
    ]
]
accept_button_template = cv2.imread('../../../resources/images/ImgFireman/AcceptButton2.png', 0)
first_extra_template = cv2.imread('../../../resources/images/ImgFireman/vyzovprynat.png', 0)
second_extra_template = cv2.imread('../../../resources/images/ImgFireman/pozarpotushen.png', 0)

excluded_regions = []


def find_template_on_screen(template, threshold=0.7):
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    for x, y in zip(loc[1], loc[0]):
        if not any(x1 <= x <= x2 and y1 <= y <= y2 for (x1, y1, x2, y2) in excluded_regions):
            return x, y
    return None


def find_accept_button_near(y_coord, threshold=0.9, tolerance=10):
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_screen, accept_button_template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    for x, y in zip(loc[1], loc[0]):
        if abs(y - y_coord) <= tolerance:
            return x, y
    excluded_regions.append((0, y_coord - tolerance, gray_screen.shape[1], y_coord + tolerance))
    return None


while True:
    print("Начало работы...")
    pyautogui.press("m")
    start_coords = find_template_on_screen(first_template)
    if start_coords:
        x, y = start_coords
        pyautogui.click(x, y)
        time.sleep(0.5)

        for idx, template in enumerate(sequence_templates, start=1):
            print(f"Поиск {idx}-й картинки...")
            step_coords = None
            while step_coords is None:
                step_coords = find_template_on_screen(template)
                time.sleep(0.5)

            x_step, y_step = step_coords
            print(f"Найдена {idx}-я картинка на координатах ({x_step}, {y_step}).")

            coordinates_coords = None
            while coordinates_coords is None:
                coordinates_coords = find_accept_button_near(y_step)
                time.sleep(0.5)

            x_coord, y_coord = coordinates_coords
            pyautogui.click(x_coord, y_coord)
            time.sleep(0.5)

            print("Запуск дополнительного поиска...")
            extra_coords = None
            while extra_coords is None:
                extra_coords = find_template_on_screen(first_extra_template)
                time.sleep(0.5)

            print(
                f"Дополнительная картинка найдена на ({extra_coords[0]}, {extra_coords[1]}), запускаем финальный поиск.")

            final_found = False
            while not final_found:
                found_final = find_template_on_screen(second_extra_template)
                if found_final:
                    print("Финальная картинка найдена! Перезапуск процесса.")
                    final_found = True
                else:
                    time.sleep(5)
