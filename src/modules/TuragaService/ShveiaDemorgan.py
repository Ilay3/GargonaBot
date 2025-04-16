import os
import sys
import time
import pyautogui
import keyboard
import argparse
import re

def get_resource_path(relative_path):
    """Корректные пути для ресурсов в любом режиме"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def find_image(image_name, confidence):
    """Оптимизированный поиск изображений"""
    image_path = get_resource_path(os.path.join('resources/images/ImgShveiaDemorgan', image_name))

    try:
        location = pyautogui.locateCenterOnScreen(
            image_path,
            confidence=confidence,
            grayscale=True,
            minSearchTime=1
        )
        return location
    except Exception:
        return None


def parse_arguments():
    """Парсинг аргументов с поддержкой --service"""
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--service", type=str, help="Сервисный режим (внутренний флаг)")
    parser.add_argument("--confidence", type=float, default=0.95)
    return parser.parse_known_args()[0]


def run_shveia_demorgan():
    """Главная функция с обработкой аргументов"""
    try:
        args = parse_arguments()

        # Конфигурация
        image_files = [f'image{i}.png' for i in range(1, 21)]
        image_config = {img: args.confidence for img in image_files}

        while True:
            keyboard.wait('e')

            # Поиск и клики
            found = {}
            for img, conf in image_config.items():
                if loc := find_image(img, conf):
                    found[img] = loc

            if not found:
                continue

            # Сортировка и обработка
            sorted_images = sorted(found.items(), key=lambda x: int(re.search(r'\d+', x[0]).group()))
            for img, (x, y) in sorted_images:
                num = int(re.search(r'\d+', img).group())
                clicks = 1 if num in (1, 20) else 2

                for _ in range(clicks):
                    pyautogui.click(x, y)
                    time.sleep(0.1)

            time.sleep(5)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run_shveia_demorgan()