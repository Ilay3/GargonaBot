import cv2
import numpy as np
import pyautogui
import time
import sys
import os
import logging
import traceback
from datetime import datetime
import platform
import requests
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# Импорт из локального модуля
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_koleso(
        templates_config=None,
        thresholds=0.9,
        check_interval=1,
        log_file="koleso.log",
        screenshot_dir="screenshots",
        telegram_enabled=True
):
    """Основная функция сервиса Koleso"""

    # Добавили отложенный импорт
    # Замените блок импорта на:
    try:
        from main import send_screenshot_to_telegram  # Прямой импорт из корня
    except ImportError as e:
        logging.error(f"Ошибка импорта Telegram модуля: {str(e)}")
        telegram_enabled = False

    # Остальной код без изменений
    def log(message, level="info"):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        if level == "info":
            logging.info(log_message)
        elif level == "error":
            logging.error(log_message + f"\n{traceback.format_exc()}")
        elif level == "warning":
            logging.warning(log_message)

    log(f"Запуск сервиса Koleso с аргументами: {sys.argv}", "info")

    if platform.system() != "Windows":
        log("Скрипт поддерживает только Windows", "error")
        return

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filemode='a',
        encoding = 'utf-8'  # Добавьте явное указание кодировки
    )
    # endregion

    # region Инициализация параметров
    pyautogui.FAILSAFE = False
    max_attempts = 5
    attempt_interval = 10
    templates = {}

    # endregion

    # region Загрузка шаблонов изображений
    def load_templates():
        nonlocal templates
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

        # Правильный путь к ресурсам
        resources_path = os.path.join(base_dir, 'resources', 'images')

        default_templates = {
            "DostupKoleso": "DostupKoleso.png",
            "IconCasino": "IconCasino.png",
            "InterfaceKolesa": "InterfaceKolesa.png",
            "ButtonKoloso": "ButtonKoloso.png"
        }

        try:
            templates_to_load = templates_config or default_templates.items()
            for name, filename in templates_to_load:
                abs_path = os.path.join(resources_path, 'ImgKoleso', filename)

                if not os.path.exists(abs_path):
                    raise FileNotFoundError(f"Template file {name} not found: {abs_path}")

                img = cv2.imread(abs_path, 0)
                templates[name] = img
                if img is None:
                    raise ValueError(f"Ошибка загрузки изображения {name}")

                templates[name] = img
                log(f"Шаблон {name} успешно загружен (размер: {img.shape})", "info")

        except Exception as e:
            log(f"Критическая ошибка загрузки шаблонов: {e}", "error")
            return False
        return True

    if not load_templates():
        return

    # endregion

    # region Вспомогательные функции
    def find_template(template_name, threshold=thresholds):
        try:
            template = templates[template_name]
            log(f"Поиск шаблона {template_name} (размер: {template.shape})", "info")

            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

            res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            log(f"Максимальное значение совпадения для {template_name}: {max_val:.2f}", "info")

            loc = np.where(res >= threshold)
            if len(loc[0]) > 0:
                y, x = loc[0][0], loc[1][0]
                log(f"Найдено совпадение {template_name} на позиции ({x}, {y})", "info")
                return (x + template.shape[1] // 2, y + template.shape[0] // 2)
            return None

        except Exception as e:
            log(f"Ошибка поиска шаблона {template_name}: {e}", "error")
            return None

    def safe_click(x, y, duration=0.2):
        try:
            log(f"Попытка клика на ({x}, {y})", "info")
            pyautogui.moveTo(x, y, duration=duration)
            pyautogui.click()
            return True
        except Exception as e:
            log(f"Ошибка при клике: {e}", "error")
            return False

    def process_step(template_name, action, attempts=max_attempts):
        log(f"Начало обработки шага {template_name}", "info")
        for attempt in range(attempts):
            log(f"Попытка {attempt + 1}/{attempts} для {template_name}", "info")
            pos = find_template(template_name)
            if pos:
                log(f"Попытка выполнить действие для {template_name}", "info")
                if action(pos):
                    log(f"Успешное выполнение для {template_name}", "info")
                    return True
                else:
                    log(f"Ошибка выполнения действия для {template_name}", "warning")
            else:
                log(f"Шаблон {template_name} не найден", "warning")
            time.sleep(attempt_interval)
        return False

    # endregion

    # region Основная логика
    log("Сервис Koleso запущен", "info")
    try:
        while True:
            try:
                log("Этап 1: Поиск DostupKoleso", "info")
                if process_step("DostupKoleso", lambda pos: (
                        time.sleep(60),
                        pyautogui.press('up'),
                        log("Нажата стрелка вверх", "info")
                )):
                    log("Этап 2: Поиск IconCasino и InterfaceKolesa", "info")
                    for step in ["IconCasino", "InterfaceKolesa"]:
                        if not process_step(step, lambda pos: safe_click(*pos)):
                            break

                    log("Этап 3: Поиск ButtonKoloso", "info")
                    if process_step("ButtonKoloso", lambda pos: safe_click(*pos)):
                        time.sleep(10)
                        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                        os.makedirs(screenshot_dir, exist_ok=True)
                        screenshot_path = os.path.join(screenshot_dir, f"{timestamp}_koleso.png")

                        try:
                            pyautogui.screenshot(screenshot_path)
                            log(f"Скриншот сохранен: {screenshot_path}", "info")
                        except Exception as e:
                            log(f"Ошибка создания скриншота: {e}", "error")

                        if telegram_enabled:
                            try:
                                if send_screenshot_to_telegram(screenshot_path):
                                    os.remove(screenshot_path)
                            except Exception as e:
                                log(f"Ошибка отправки в Telegram: {e}", "error")

                        time.sleep(20)
                        pyautogui.press('esc')
                        time.sleep(1)
                        pyautogui.press('esc')
                        pyautogui.press('backspace')

                time.sleep(check_interval)

            except KeyboardInterrupt:
                log("Работа прервана пользователем", "info")
                break

            except Exception as e:
                log(f"Критическая ошибка в основном цикле: {str(e)}\n{traceback.format_exc()}", "error")
                time.sleep(attempt_interval)

    finally:
        log("Сервис Koleso остановлен", "info")
    # endregion


if __name__ == "__main__":
    try:
        print(f"Полученные аргументы: {sys.argv}", "info")
        if any("--service=koleso" in arg for arg in sys.argv):
            run_koleso(
                thresholds=0.9,
                check_interval=1,
                telegram_enabled=True
            )
        else:
            print("Для запуска сервиса используйте флаг --service=koleso")
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}\n{traceback.format_exc()}")