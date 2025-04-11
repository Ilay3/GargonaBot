import cv2
import numpy as np
import pyautogui
import time
import sys
import os
import logging
from datetime import datetime
import platform


def run_stroyka(
        button_e_path=None,
        button_f_path=None,
        button_y_path=None,
        threshold=0.8,
        check_interval=1 / 32,
        log_file="stroyka.log"
):
    """
    Исправленная версия с правильной настройкой путей
    """

    def log(message, level="info"):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        if level == "info":
            logging.info(log_message)
        elif level == "error":
            logging.error(log_message)

    # Проверка ОС
    if platform.system() != "Windows":
        log("Скрипт поддерживает только Windows.", "error")
        return

    # Инициализация логирования
    pyautogui.FAILSAFE = False
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Определение базовой директории
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        # Новый правильный путь к корню проекта
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")

    log(f"Базовая директория: {base_dir}")

    # Конфигурация шаблонов
    templates_config = {
        "ButtonE": {
            "path": button_e_path or os.path.join(base_dir, "resources", "images", "ImgStroyka", "ButtonE.png"),
            "key": "e"
        },
        "ButtonF": {
            "path": button_f_path or os.path.join(base_dir, "resources", "images", "ImgStroyka", "ButtonF.png"),
            "key": "f"
        },
        "ButtonY": {
            "path": button_y_path or os.path.join(base_dir, "resources", "images", "ImgStroyka", "ButtonY.png"),
            "key": "y"
        }
    }

    # Загрузка шаблонов с отладочным выводом
    templates = {}
    for name, config in templates_config.items():
        try:
            full_path = os.path.abspath(config["path"])
            log(f"Ожидаемый путь к {name}: {full_path}")  # Отладочная информация

            if not os.path.exists(full_path):
                log(f"Файл шаблона {name} не найден: {full_path}", "error")
                return

            template = cv2.imread(full_path, 0)
            if template is None:
                raise ValueError(f"Не удалось загрузить шаблон {name}")

            templates[name] = {
                "template": template,
                "key": config["key"]
            }
            log(f"Шаблон {name} успешно загружен")
        except Exception as e:
            log(f"Ошибка загрузки {name}: {str(e)}", "error")
            return

    def find_template_on_screen():
        """Поиск всех шаблонов на экране с обработкой ошибок"""
        try:
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

            for name, data in templates.items():
                res = cv2.matchTemplate(gray_screen, data["template"], cv2.TM_CCOEFF_NORMED)
                if np.any(res >= threshold):
                    return name
            return None
        except Exception as e:
            log(f"Ошибка поиска шаблонов: {str(e)}", "error")
            return None

    log("Сервис Stroyka запущен...")
    try:
        while True:
            try:
                found_template = find_template_on_screen()
                if found_template:
                    key = templates[found_template]["key"]
                    log(f"Обнаружен {found_template}, нажатие клавиши {key}")
                    pyautogui.press(key)
                time.sleep(check_interval)
            except KeyboardInterrupt:
                log("Прерывание пользователем", "info")
                break
            except Exception as e:
                log(f"Ошибка в основном цикле: {str(e)}", "error")
                time.sleep(5)
    finally:
        log("Сервис Stroyka остановлен")


if __name__ == "__main__":
    if "--service=stroyka" in sys.argv:
        run_stroyka()
    else:
        print("Требуется флаг --service=stroyka")