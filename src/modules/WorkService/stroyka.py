import cv2
import numpy as np
import pyautogui
import time
import sys
import os
import platform


def run_stroyka(
        button_e_path=None,
        button_f_path=None,
        button_y_path=None,
        threshold=0.95,
        check_interval=1/32
):
    # Проверка ОС
    if platform.system() != "Windows":
        return

    # Инициализация параметров
    pyautogui.FAILSAFE = False

    # Определение базовой директории
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")

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

    # Загрузка шаблонов
    templates = {}
    for name, config in templates_config.items():
        try:
            full_path = os.path.abspath(config["path"])
            if not os.path.exists(full_path):
                return

            template = cv2.imread(full_path, 0)
            if template is None:
                raise ValueError()

            templates[name] = {
                "template": template,
                "key": config["key"]
            }
        except Exception:
            return

    def find_template_on_screen():
        """Поиск всех шаблонов на экране"""
        try:
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

            for name, data in templates.items():
                res = cv2.matchTemplate(gray_screen, data["template"], cv2.TM_CCOEFF_NORMED)
                if np.any(res >= threshold):
                    return name
            return None
        except Exception:
            return None

    try:
        while True:
            try:
                found_template = find_template_on_screen()
                if found_template:
                    key = templates[found_template]["key"]
                    pyautogui.press(key)
                time.sleep(check_interval)
            except KeyboardInterrupt:
                break
            except Exception:
                time.sleep(5)
    finally:
        pass


if __name__ == "__main__":
    if "--service=stroyka" in sys.argv:
        run_stroyka()
    else:
        print("Требуется флаг --service=stroyka")