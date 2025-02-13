import cv2
import numpy as np
import pyautogui
import time
import keyboard  # Для отслеживания нажатия клавиши

# Загружаем эталонные изображения (картинки для поиска)
first_template = cv2.imread('../../../resources/images/ImgFireman/StartButton1.png', 0)
sequence_templates = [
    (cv2.imread(path, 0), path.split('/')[-1]) for path in [
        '../../../resources/images/ImgFireman/0iz2.png',  # Картинка для поиска 1
        '../../../resources/images/ImgFireman/0iz2.png',  # Картинка для поиска 2
        '../../../resources/images/ImgFireman/RoadAvary.png',  # Картинка для поиска 3
        '../../../resources/images/ImgFireman/ForestAvary.png'  # Картинка для поиска 4
    ]
]

# Картинка для кнопки принятия
accept_button_template = cv2.imread('../../../resources/images/ImgFireman/AcceptButton2.png', 0)

# Дополнительные картинки для поиска

second_extra_template = cv2.imread('../../../resources/images/ImgFireman/pozarpotushen.png', 0)

# Загружаем 4 картинки для проверки доступности заказа
check_templates = [
    cv2.imread('../../../resources/images/ImgFireman/verify/0iz2.png', 0),
    cv2.imread('../../../resources/images/ImgFireman/verify/1iz2.png', 0),
    cv2.imread('../../../resources/images/ImgFireman/verify/1iz1.png', 0),
    cv2.imread('../../../resources/images/ImgFireman/verify/1iz1.png', 0),
]

check_for_templates = [
    [check_templates[0], check_templates[1]],
    [check_templates[0], check_templates[1]],
    [check_templates[2]],
    [check_templates[3]],
]

# Исключенные области экрана (если необходимо)
excluded_regions = []


def find_template_on_screen(template, threshold=0.9):
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    if len(loc[0]) == 0:  # Если совпадений не найдено
        print("Шаблон не найден на экране.")

    for x, y in zip(loc[1], loc[0]):
        if not any(x1 <= x <= x2 and y1 <= y <= y2 for (x1, y1, x2, y2) in excluded_regions):
            return x, y
    return None


def find_accept_button_near(y_coord, threshold=0.98, tolerance=10):
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_screen, accept_button_template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    for x, y in zip(loc[1], loc[0]):
        if abs(y - y_coord) <= tolerance:
            return x, y
    return None


def verify_order(image, check_images, threshold=0.95):
    if len(image.shape) > 2:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    for check_image in check_images:
        if len(check_image.shape) > 2:
            check_image = cv2.cvtColor(check_image, cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(image, check_image, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        if max_val >= threshold:
            print(f"Заказ доступен! Картинка для проверки найдена.")
            return True
    print("Заказ недоступен.")
    return False


def find_start_button(threshold=0.9):
    """
    Функция для поиска кнопки StartButton с возможностью настройки точности поиска.
    :param threshold: Пороговое значение для matchTemplate, по умолчанию 0.9.
    :return: Координаты кнопки StartButton или None, если не найдена.
    """
    print(f"Ищем StartButton с точностью {threshold}...")
    start_coords = find_template_on_screen(first_template, threshold)
    return start_coords


while True:
    print("Начало работы...")
    start_coords = find_start_button(threshold=0.85)  # Попробуем уменьшить точность
    if start_coords:
        x, y = start_coords
        print(f"Найдена кнопка StartButton на координатах ({x}, {y}).")
        pyautogui.click(x, y)
        time.sleep(0.5)

        for idx, (template, name) in enumerate(sequence_templates, start=1):
            print(f"Поиск картинки: {name}...")
            step_coords = None
            start_time = time.time()
            while step_coords is None:
                step_coords = find_template_on_screen(template)
                time.sleep(0.5)
                if time.time() - start_time > 2:
                    print(f"Картинка {name} не найдена за 2 секунды.")
                    break

            if step_coords is None:
                continue

            x_step, y_step = step_coords
            print(f"Найдена картинка {name} на координатах ({x_step}, {y_step}).")

            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            while not verify_order(screenshot, check_for_templates[idx - 1]):
                print(f"Заказ для {name} недоступен. Ищем следующую картинку...")
                step_coords = None
                while step_coords is None:
                    idx += 1
                    if idx > len(sequence_templates):
                        print("Все картинки проверены.")
                        break
                    template, name = sequence_templates[idx - 1]
                    step_coords = find_template_on_screen(template)
                    time.sleep(0.5)
                if step_coords is None:
                    break

            if step_coords is None:
                continue

            x_step, y_step = step_coords
            print(f"Найдена подходящая картинка {name} на координатах ({x_step}, {y_step}).")

            accept_coords = find_accept_button_near(y_step)
            if accept_coords:
                x_accept, y_accept = accept_coords
                print(f"Найдена кнопка принятия на координатах ({x_accept}, {y_accept}).")
                pyautogui.click(x_accept, y_accept)
                time.sleep(0.5)

                print("Ищем картинку pozarpotushen.png...")
                extra_coords = None
                while extra_coords is None:
                    extra_coords = find_template_on_screen(second_extra_template)
                    time.sleep(0.5)

                if extra_coords:
                    print(f"Картинка pozarpotushen.png найдена на координатах {extra_coords}.")
                    break
                else:
                    print("Не удалось найти картинку pozarpotushen.png.")

    if keyboard.is_pressed('k'):
        print("Выход из программы...")
        break
