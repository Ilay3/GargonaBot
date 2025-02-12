import cv2
import numpy as np
import pyautogui
import time

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

# Координаты области поиска (задать вручную)
x1, y1, x2, y2 = 922, 902, 992, 963  # Примерные координаты


def find_template_in_region(template, region, threshold=0.8):
    """Ищет шаблон в указанной области экрана."""
    screenshot = pyautogui.screenshot(region=region)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    return len(loc[0]) > 0


# Бесконечный цикл поиска
while True:
    region = (x1, y1, x2 - x1, y2 - y1)
    for path, template in templates.items():
        if find_template_in_region(template, region):
            pyautogui.press(image_key_map[path])
            print(f"Обнаружено {path}, нажата клавиша {image_key_map[path]}")
            time.sleep(0.001)  # Задержка 1 мс
    time.sleep(0.01)  # Основной цикл с небольшой задержкой
