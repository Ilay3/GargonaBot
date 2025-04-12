import os
import time
import logging
import sys
import platform
from datetime import datetime
import pyautogui
import cv2
import numpy as np
import traceback

pyautogui.FAILSAFE = False


def get_resource_path(relative_path):
    """Определение корректных путей для ресурсов"""
    try:
        base_path = sys._MEIPASS  # Для упакованного .exe
    except AttributeError:
        base_path = os.path.abspath(".")  # Для разработки
    return os.path.join(base_path, relative_path)


def load_templates(image_dir):
    """Загрузка всех PNG изображений из указанной директории"""
    templates = {}
    try:
        full_path = get_resource_path(image_dir)

        if not os.path.exists(full_path):
            logging.error(f"Директория не найдена: {full_path}")
            return None

        for filename in os.listdir(full_path):
            if filename.lower().endswith('.png'):
                file_path = os.path.join(full_path, filename)
                if os.path.getsize(file_path) == 0:
                    logging.error(f"Пустой файл: {file_path}")
                    continue

                img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    logging.error(f"Ошибка чтения: {file_path}")
                    continue

                templates[filename] = img
                logging.debug(f"Загружен шаблон: {filename} ({img.shape[1]}x{img.shape[0]})")

        return templates

    except Exception as e:
        logging.critical(f"Ошибка загрузки шаблонов: {str(e)}")
        traceback.print_exc()
        return None


def run_tochilka(
        image_dir='resources/images/ImgTochilka',
        confidence=0.8,
        search_region=(657, 670, 1260, 977),
        offset_x=20,
        offset_y=50,
        check_interval=0.001,
        log_file=None
):
    """Основная функция для поиска и перемещения курсора"""

    def log(message, level="info"):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        if level == "info":
            logging.info(log_message)
        elif level == "error":
            logging.error(log_message)
        elif level == "debug":
            logging.debug(log_message)

    if platform.system() != "Windows":
        log("Скрипт поддерживает только Windows.", "error")
        return

    if log_file is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.join(base_dir, "..", "..", "..", "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "tochilka_log.txt")

    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )

    log("Запуск сервиса Tochilka...")
    templates = load_templates(image_dir)

    if not templates:
        log("Ошибка загрузки шаблонов", "error")
        return

    def find_image(image_name, confidence_level, region=None):
        """Поиск изображения с учетом области поиска"""
        template = templates.get(image_name)
        if template is None:
            log(f"Шаблон {image_name} не загружен", "error")
            return None

        try:
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()

            gray_screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
            res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= confidence_level)

            if len(loc[0]) > 0:
                y, x = loc[0][0], loc[1][0]
                if region:
                    x += region[0]
                    y += region[1]
                # Возвращаем верхний левый угол совпадения
                return (x, y, template.shape[1], template.shape[0])
            return None

        except Exception as e:
            log(f"Ошибка поиска: {str(e)}", "error")
            return None

    try:
        log("Сервис активен. Начало обработки...")
        while True:
            try:
                for image_name in templates.keys():
                    result = find_image(image_name, confidence, search_region)
                    if result:
                        x, y, w, h = result
                        # Вычисляем целевую позицию с смещением
                        target_x = x + offset_x
                        target_y = y + offset_y
                        log(f"Перемещение к ({target_x}, {target_y})", "debug")
                        pyautogui.moveTo(target_x, target_y, duration=0.01)

                time.sleep(check_interval)

            except KeyboardInterrupt:
                log("Прерывание пользователем", "info")
                break

            except Exception as e:
                log(f"Ошибка в основном цикле: {str(e)}", "error")
                time.sleep(1)

    finally:
        log("Остановка сервиса Tochilka")


if __name__ == "__main__":
    if "--service" in sys.argv:
        run_tochilka()
    else:
        print("Для запуска сервиса используйте флаг --service")