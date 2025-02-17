import cv2
import numpy as np
import keyboard  # Быстрее, чем pyautogui
import time
import mss



# Путь к изображениям и соответствующие кнопки
image_key_map = {
    '../../../resources/images/ImgKachalka/Circle1.png': 'space',
    '../../../resources/images/ImgKachalka/Circle2.png': 'space'  # Добавлен новый шаблон
}

# Загружаем все шаблоны и проверяем их
templates = {}
for path in image_key_map:
    template = cv2.imread(path, 0)
    if template is None:
        print(f"Ошибка: не удалось загрузить {path}")
    else:
        templates[path] = template

# Координаты области поиска
x1, y1, x2, y2 = 772, 607, 1123, 906  # Примерные координаты
region = {"top": y1, "left": x1, "width": x2 - x1, "height": y2 - y1}

# Захват экрана через mss
sct = mss.mss()


def find_template_in_region(template, screenshot_gray, threshold=0.8):
    """Ищет шаблон в указанной области экрана."""
    h_t, w_t = template.shape[:2]
    h_s, w_s = screenshot_gray.shape[:2]

    # Проверка, что шаблон не больше изображения
    if h_t > h_s or w_t > w_s:
        print(f"Ошибка: шаблон ({w_t}x{h_t}) больше, чем изображение ({w_s}x{h_s})")
        return False

    # Сравнение шаблона с областью
    res = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
    return np.any(res >= threshold)


while True:
    start_time = time.time()

    # Быстрый скриншот через mss
    screenshot = np.array(sct.grab(region))[:, :, :3]  # Убираем альфа-канал
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    keys_to_press = set()  # Используем set, чтобы избежать дубликатов

    for path, template in templates.items():
        if find_template_in_region(template, screenshot_gray):
            key = image_key_map[path]
            keys_to_press.add(key)

    # Нажимаем все найденные клавиши сразу
    for key in keys_to_press:
        keyboard.press(key)

    time.sleep(0.005)  # Минимальная задержка

    # Отпускаем все клавиши
    for key in keys_to_press:
        keyboard.release(key)

    elapsed = time.time() - start_time
    if elapsed < 0.001:
        time.sleep(0.001 - elapsed)  # Подстройка времени
