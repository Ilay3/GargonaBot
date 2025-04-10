import cv2
import numpy as np
import pyautogui
import time
import sys
import os
import logging
from datetime import datetime
import platform


def run_waxta(
        image_path=None,
        key_to_press='e',
        threshold=0.9,
        check_interval=1 / 32,
        log_file="waxta.log"
):
    """
    Улучшенный сервис поиска шаблона на экране с обработкой ошибок и логированием.
    """

    # Настройка логирования
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

    # Инициализация параметров
    pyautogui.FAILSAFE = False
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Загрузка изображения шаблона
    if image_path is None:
        if getattr(sys, 'frozen', False):
            # Путь для исполняемого файла (PyInstaller)
            base_dir = sys._MEIPASS
        else:
            # Путь для обычного скрипта
            base_dir = os.path.dirname(os.path.abspath(__file__))

        image_path = os.path.join(
            base_dir, "resources", "images", "ImgWaxta", "ButtonE.png"
        )

    image_path = os.path.abspath(image_path)
    log(f"Ожидаемый путь к шаблону: {image_path}")  # <-- Добавить эту строку
    if not os.path.exists(image_path):
        log(f"Файл шаблона не найден: {image_path}", "error")
        return

    try:
        template = cv2.imread(image_path, 0)
        if template is None:
            raise ValueError("Не удалось загрузить изображение")
    except Exception as e:
        log(f"Ошибка загрузки шаблона: {e}", "error")
        return

    log(f"Шаблон успешно загружен: {image_path}")

    def find_template_on_screen():
        """Поиск шаблона на экране с обработкой ошибок."""
        try:
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
            return np.any(res >= threshold)
        except Exception as e:
            log(f"Ошибка поиска шаблона: {e}", "error")
            return False

    log("Сервис Waxta запущен...")
    try:
        while True:
            try:
                if find_template_on_screen():
                    log("Шаблон обнаружен, начинаю нажатия...")
                    while find_template_on_screen():
                        pyautogui.press(key_to_press)
                        time.sleep(check_interval)
                time.sleep(1)
            except KeyboardInterrupt:
                log("Прерывание пользователем")
                break
            except Exception as e:
                log(f"Ошибка в основном цикле: {e}", "error")
                time.sleep(5)  # Задержка перед повторной попыткой
    finally:
        log("Сервис Waxta остановлен")


if __name__ == "__main__":
    if "--service" in sys.argv:
        run_waxta()
    else:
        print("Флаг --service не передан, выход из программы.")