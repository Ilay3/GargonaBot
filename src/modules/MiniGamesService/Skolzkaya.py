import cv2
import numpy as np
import keyboard  # Быстрее чем pyautogui
import time
import mss

# Путь к изображениям и соответствующие кнопки
image_key_map = {
    '../../../resources/images/ImgMiniGames/W.png': 'w',
    '../../../resources/images/ImgMiniGames/A.png': 'a',
    '../../../resources/images/ImgMiniGames/S.png': 's',
    '../../../resources/images/ImgMiniGames/D.png': 'd',
    '../../../resources/images/ImgMiniGames/Up.png': 'up',
    '../../../resources/images/ImgMiniGames/Down.png': 'down',
    '../../../resources/images/ImgMiniGames/Right.png': 'right',
    '../../../resources/images/ImgMiniGames/Left.png': 'left'
}

# Загружаем все шаблоны
templates = {path: cv2.imread(path, 0) for path in image_key_map}

# Координаты области поиска
x1, y1, x2, y2 = 922, 902, 992, 963  # Примерные координаты
region = {"top": y1, "left": x1, "width": x2 - x1, "height": y2 - y1}

# Захват экрана через mss
sct = mss.mss()


def find_template_in_region(template, screenshot_gray, threshold=0.8):
    """Ищет шаблон в указанной области экрана."""
    res = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
    return np.any(res >= threshold)


while True:
    start_time = time.time()

    # Быстрый скриншот через mss
    screenshot = np.array(sct.grab(region))[:, :, :3]  # Убираем альфа-канал
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    keys_to_press = []  # Список клавиш для одновременного нажатия

    for path, template in templates.items():
        if find_template_in_region(template, screenshot_gray):
            key = image_key_map[path]
            keys_to_press.append(key)

    # Нажимаем все найденные клавиши сразу
    for key in keys_to_press:
        keyboard.press(key)

    time.sleep(0.005)  # Минимальная задержка (можно уменьшить до 0.005)

    # Отпускаем все клавиши
    for key in keys_to_press:
        keyboard.release(key)

    elapsed = time.time() - start_time
    if elapsed < 0.001:
        time.sleep(0.001 - elapsed)  # Подстройка времени