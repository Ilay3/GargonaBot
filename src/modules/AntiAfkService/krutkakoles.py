import cv2
import numpy as np
import pyautogui
import time
import sys
import os
import traceback
from datetime import datetime
import platform
import json

sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__

def get_base_path():
    """Возвращает корректный путь к ресурсам для EXE и исходного кода"""
    if getattr(sys, 'frozen', False):
        # Путь при запуске из EXE
        return sys._MEIPASS
    else:
        # Путь при запуске из исходного кода
        return os.path.dirname(os.path.abspath(__file__))
def send_screenshot_to_telegram(screenshot_path, message=None):
    try:
        from main import send_screenshot_to_telegram as _send
        return _send(screenshot_path, message)
    except ImportError:
        return False
    except Exception as e:
        print(f"Telegram error: {str(e)}")
        return False


def run_koleso(
        thresholds=0.9,
        check_interval=1,
        screenshot_dir="screenshots",
        result_check_attempts=10
):
    print("\n" + "=" * 40)
    print(f"[{datetime.now()}] Starting Koleso service")
    print(f"Threshold: {thresholds}")
    print(f"Check interval: {check_interval}s")
    print("=" * 40)

    if platform.system() != "Windows":
        print("Windows required!")
        return

    # Проверка прав записи
    try:
        test_file = os.path.join(screenshot_dir, "test_koleso.txt")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        print("Write test: OK")
    except Exception as e:
        print(f"Write error: {str(e)}")
        return

    pyautogui.FAILSAFE = False
    templates = {}

    def load_templates():
        print("\nLoading templates...")
        base_dir = get_base_path()
        resources_path = os.path.join(
            base_dir,
            'resources',
            'images',
            'ImgKoleso'
        )

        print(f"Resource path: {resources_path}")

        template_files = {
            "DostupKoleso": "DostupKoleso.png",
            "IconCasino": "IconCasino.png",
            "InterfaceKolesa": "InterfaceKolesa.png",
            "ButtonKoloso": "ButtonKoloso.png",
            "ResultKoleso": "ResultKoleso.png"
        }

        for name, filename in template_files.items():
            path = os.path.join(resources_path, filename)
            print(f"Loading: {path}")

            if not os.path.exists(path):
                print(f"File not found: {path}")
                return False

            img = cv2.imread(path, 0)
            if img is not None:
                templates[name] = img
                print(f"Loaded {name} ({img.shape[1]}x{img.shape[0]})")
            else:
                print(f"Failed to load: {filename}")
                return False
        return True

    def find_template(template_name, threshold=thresholds):
        try:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Searching: {template_name}")
            template = templates[template_name]
            screenshot = pyautogui.screenshot()
            gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2GRAY)

            res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            print(f"Match value: {max_val:.2f} (need {threshold})")

            if max_val >= threshold:
                y, x = max_loc
                center_x = x + template.shape[1] // 2
                center_y = y + template.shape[0] // 2
                print(f"Found at ({center_x}, {center_y})")
                return (center_x, center_y)
            print("Not found")
            return None
        except Exception as e:
            print(f"Search error: {str(e)}")
            traceback.print_exc()
            return None

    def safe_click(x, y, duration=0.2):
        try:
            print(f"Clicking ({x}, {y})")
            pyautogui.moveTo(x, y, duration=duration)
            pyautogui.click()
            return True
        except Exception as e:
            print(f"Click failed: {str(e)}")
            return False

    def process_step(name, action, attempts=5):
        print(f"\n-- Processing {name} --")
        for attempt in range(1, attempts + 1):
            print(f"Attempt {attempt}/{attempts}")
            pos = find_template(name)
            if pos:
                print("Executing action")
                if action(pos):
                    print("Action success")
                    return True
                print("Action failed")
            time.sleep(10)
        print("All attempts failed")
        return False

    try:
        print("\nChecking settings...")
        settings_path = os.path.join(os.path.dirname(__file__), '..', 'settings.json')
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                settings = json.load(f)
                print("Settings loaded")
        else:
            print("No settings file")

        while True:
            try:
                print("\n" + "-" * 30)
                print(f"New cycle {datetime.now().strftime('%H:%M:%S')}")

                if process_step("DostupKoleso", lambda pos: (
                        time.sleep(65),
                        pyautogui.press('up')
                )):
                    for step in ["IconCasino", "InterfaceKolesa"]:
                        if not process_step(step, lambda pos: safe_click(*pos)):
                            break

                    if process_step("ButtonKoloso", lambda pos: safe_click(*pos)):
                        if process_step("ResultKoleso", lambda pos: True, 15):
                            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                            os.makedirs(screenshot_dir, exist_ok=True)
                            path = os.path.join(screenshot_dir, f"koleso_{timestamp}.png")

                            try:
                                pyautogui.screenshot(path)
                                print(f"Screenshot saved: {path}")

                                if send_screenshot_to_telegram(path, "Koleso result"):
                                    print("Telegram sent")
                                    os.remove(path)
                                else:
                                    print("Telegram failed")
                            except Exception as e:
                                print(f"Screenshot error: {str(e)}")

                        print("Resetting...")
                        time.sleep(20)
                        pyautogui.press('esc')
                        pyautogui.press('esc')
                        pyautogui.press('backspace')

                print(f"Waiting {check_interval}s")
                time.sleep(check_interval)

            except KeyboardInterrupt:
                print("Stopped by user")
                break

            except Exception as e:
                print(f"Cycle error: {str(e)}")
                traceback.print_exc()
                time.sleep(10)

    finally:
        print("\n" + "=" * 40)
        print(f"[{datetime.now()}] Service stopped")
        print("=" * 40)


if __name__ == "__main__":
    if "--service=koleso" in sys.argv:
        run_koleso()
    else:
        print("Use --service=koleso to start")