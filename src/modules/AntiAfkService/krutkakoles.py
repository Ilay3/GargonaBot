import cv2
import numpy as np
import pyautogui
import time
import sys
import os
import traceback
from datetime import datetime
import platform
import requests
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_koleso(
        templates_config=None,
        thresholds=0.9,
        check_interval=1,
        screenshot_dir="screenshots",
        telegram_enabled=True
):
    try:
        from main import send_screenshot_to_telegram
    except ImportError:
        telegram_enabled = False

    if platform.system() != "Windows":
        return

    pyautogui.FAILSAFE = False
    max_attempts = 5
    attempt_interval = 10
    templates = {}

    def load_templates():
        nonlocal templates
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
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
                img = cv2.imread(abs_path, 0)
                templates[name] = img

        except Exception:
            return False
        return True

    if not load_templates():
        return

    def find_template(template_name, threshold=thresholds):
        try:
            template = templates[template_name]
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

            res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= threshold)
            if len(loc[0]) > 0:
                y, x = loc[0][0], loc[1][0]
                return (x + template.shape[1] // 2, y + template.shape[0] // 2)
            return None

        except Exception:
            return None

    def safe_click(x, y, duration=0.2):
        try:
            pyautogui.moveTo(x, y, duration=duration)
            pyautogui.click()
            return True
        except Exception:
            return False

    def process_step(template_name, action, attempts=max_attempts):
        for attempt in range(attempts):
            pos = find_template(template_name)
            if pos:
                if action(pos):
                    return True
            time.sleep(attempt_interval)
        return False

    try:
        while True:
            try:
                if process_step("DostupKoleso", lambda pos: (
                        time.sleep(5),
                        pyautogui.press('up')
                )):
                    for step in ["IconCasino", "InterfaceKolesa"]:
                        if not process_step(step, lambda pos: safe_click(*pos)):
                            break

                    if process_step("ButtonKoloso", lambda pos: safe_click(*pos)):
                        time.sleep(5)
                        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                        os.makedirs(screenshot_dir, exist_ok=True)
                        screenshot_path = os.path.join(screenshot_dir, f"{timestamp}_koleso.png")

                        try:
                            pyautogui.screenshot(screenshot_path)
                        except Exception:
                            pass

                        if telegram_enabled:
                            try:
                                if send_screenshot_to_telegram(screenshot_path):
                                    os.remove(screenshot_path)
                            except Exception:
                                pass

                        time.sleep(20)
                        pyautogui.press('esc')
                        time.sleep(1)
                        pyautogui.press('esc')
                        pyautogui.press('backspace')

                time.sleep(check_interval)

            except KeyboardInterrupt:
                break

            except Exception:
                time.sleep(attempt_interval)

    finally:
        pass

if __name__ == "__main__":
    try:
        if any("--service=koleso" in arg for arg in sys.argv):
            run_koleso(
                thresholds=0.9,
                check_interval=1
            )
        else:
            print("Для запуска сервиса используйте флаг --service=koleso")
    except Exception:
        pass