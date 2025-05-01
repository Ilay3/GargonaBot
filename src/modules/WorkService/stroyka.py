import cv2
import numpy as np
import pyautogui
import time
import sys
import os
import platform
import ctypes
import threading


def run_stroyka(
        button_e_path=None,
        button_f_path=None,
        button_y_path=None,
        threshold=0.85,
        check_interval=0.08,
        lost_threshold=2,
        press_repeats=3,
        press_delay=0.03
):
    print("[INFO] Запуск службы Стройка (оптимизированная версия)")

    search_started = False
    current_target = None
    lost_count = 0

    def show_error_and_exit():
        print("[ERROR] Критическая ошибка: Поиск изображений не начался в течение 30 секунд")
        ctypes.windll.user32.MessageBoxW(
            0,
            "Из-за недостаточной производительности компьютера бот не может продолжить работу с функцией 'Стройка'.\n\n"
            "Рекомендуемые действия:\n"
            "1. Закройте ресурсоемкие приложения\n"
            "2. Уменьшите разрешение экрана\n"
            "3. Обратитесь в техническую поддержку",
            "Ошибка производительности",
            0x1000
        )
        os._exit(1)

    def start_search_checker():
        time.sleep(30)
        if not search_started:
            show_error_and_exit()

    checker_thread = threading.Thread(target=start_search_checker, daemon=True)
    checker_thread.start()

    try:
        screen_size = pyautogui.size()
        print(f"[DEBUG] Разрешение экрана: {screen_size.width}x{screen_size.height}")
    except Exception as e:
        print(f"[ERROR] Ошибка получения информации об экране: {str(e)}")

    if platform.system() != "Windows":
        print("[ERROR] Скрипт работает только на Windows")
        return

    pyautogui.FAILSAFE = False
    print("[INFO] Инициализация параметров выполнена")

    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")

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

    templates = {}
    for name, config in templates_config.items():
        try:
            full_path = os.path.abspath(config["path"])
            if not os.path.exists(full_path):
                print(f"[ERROR] Файл шаблона не найден: {full_path}")
                return

            template = cv2.imread(full_path, 0)
            if template is None:
                print(f"[ERROR] Ошибка загрузки изображения: {full_path}")
                raise ValueError()

            templates[name] = {
                "template": template,
                "key": config["key"],
                "size": template.shape[::-1]
            }
            print(f"[INFO] Успешно загружен шаблон: {name}")
        except Exception as e:
            print(f"[ERROR] Ошибка при загрузке шаблона {name}: {str(e)}")
            return

    def find_template(target_name=None, screenshot=None):
        nonlocal search_started
        search_started = True

        try:
            if screenshot is None:
                screenshot = pyautogui.screenshot()

            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            gray_screen = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)

            if target_name:
                data = templates[target_name]
                res = cv2.matchTemplate(gray_screen, data["template"], cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(res)
                return max_val >= threshold

            else:
                best_match = {"name": None, "value": 0}
                for name, data in templates.items():
                    res = cv2.matchTemplate(gray_screen, data["template"], cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, _ = cv2.minMaxLoc(res)
                    if max_val > best_match["value"]:
                        best_match = {"name": name, "value": max_val}

                return best_match["name"] if best_match["value"] >= threshold else None

        except Exception as e:
            print(f"[ERROR] Ошибка при поиске шаблонов: {str(e)}")
            return None

    try:
        print("[INFO] Начало основного цикла")
        cycle_counter = 0
        last_screenshot_time = 0
        screenshot_cache = None
        cache_valid_time = 0.1

        while True:
            cycle_counter += 1
            try:
                current_time = time.time()

                if current_time - last_screenshot_time > cache_valid_time:
                    screenshot_cache = pyautogui.screenshot()
                    last_screenshot_time = current_time

                if current_target:
                    target_found = find_template(current_target, screenshot_cache)

                    if target_found:
                        lost_count = 0
                        print(f"[ACTION] Быстрые нажатия ({press_repeats}x): {templates[current_target]['key']}")
                        for _ in range(press_repeats):
                            pyautogui.press(templates[current_target]['key'])
                            time.sleep(press_delay)
                        time.sleep(check_interval * 0.7)
                    else:
                        lost_count += 1
                        if lost_count >= lost_threshold:
                            print(f"[INFO] Цель {current_target} утеряна")
                            current_target = None
                            lost_count = 0
                        time.sleep(check_interval * 0.5)

                else:
                    found_template = find_template(None, screenshot_cache)
                    if found_template:
                        current_target = found_template
                        print(f"[INFO] Новая цель: {current_target}")
                        for _ in range(press_repeats):
                            pyautogui.press(templates[current_target]['key'])
                            time.sleep(press_delay)
                        time.sleep(check_interval * 0.5)

                time.sleep(check_interval)

            except KeyboardInterrupt:
                print("[INFO] Получен сигнал KeyboardInterrupt")
                break

            except Exception as e:
                print(f"[CRITICAL] Критическая ошибка: {str(e)}")
                time.sleep(1)

    except Exception as e:
        print(f"[CRITICAL] Критическая ошибка: {str(e)}")
    finally:
        print("[INFO] Завершение работы службы Стройка")


if __name__ == "__main__":
    if "--service=stroyka" in sys.argv:
        run_stroyka(
            press_repeats=4,
            press_delay=0.02,
            check_interval=0.06
        )
    else:
        print("Требуется флаг --service=stroyka")