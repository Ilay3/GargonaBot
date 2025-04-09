import cv2
import numpy as np
import keyboard
import time
import mss
import os
import sys
from datetime import datetime

def get_resource_path(relative_path):
    """Корректно определяет путь к ресурсам при упаковке и обычном запуске."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_path, relative_path)
    return full_path.replace('\\', os.sep) if os.sep == '/' else full_path.replace('/', os.sep)

def log(message):
    """Выводит сообщение с временной меткой."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def run_Skolzkaya(
        search_region=(922, 902, 992, 963),
        threshold=0.8,
):
    log("Функция run_Skolzkaya запущена.")
    x1, y1, x2, y2 = search_region
    region = {"top": y1, "left": x1, "width": x2 - x1, "height": y2 - y1}

    sct = mss.mss()

    image_key_map = {
        "W": "w",
        "A": "a",
        "S": "s",
        "D": "d",
        "Up": "up",
        "Down": "down",
        "Right": "right",
        "Left": "left"
    }

    templates = {}
    for name in image_key_map:
        path = get_resource_path(f"resources/images/ImgMiniGames/{name}.png")
        if not os.path.exists(path):
            log(f"[ОШИБКА] Файл не найден: {path}")
            return
        image = cv2.imread(path, 0)
        if image is None:
            log(f"[ОШИБКА] Невозможно загрузить изображение: {path}")
            return
        templates[name] = image
        log(f"[ЗАГРУЗКА] {name}: успешно загружено ({image.shape})")

    def find_template_in_region(template, screenshot_gray):
        """Проверяет наличие шаблона на скриншоте."""
        res = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        return np.any(res >= threshold)

    log("Основной цикл запущен...")

    while True:
        start_time = time.time()

        screenshot = np.array(sct.grab(region))[:, :, :3]
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        keys_to_press = []

        for name, template in templates.items():
            if find_template_in_region(template, screenshot_gray):
                key = image_key_map[name]
                keys_to_press.append(key)
                log(f"[НАЖАТИЕ] Обнаружено {name} -> нажатие {key}")

        for key in keys_to_press:
            keyboard.press(key)

        time.sleep(0.005)

        for key in keys_to_press:
            keyboard.release(key)

        elapsed = time.time() - start_time
        if elapsed < 0.001:
            time.sleep(0.001 - elapsed)

if __name__ == "__main__":
    log("Skolzkaya.py: запуск как скрипта.")
    if "--service=skolzkaya" in sys.argv:
        log("--service=skolzkaya найден, запускается run_Skolzkaya()")
        run_Skolzkaya()
    else:
        log("Флаг --service=skolzkaya не найден. Завершение.")
