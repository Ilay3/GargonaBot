import cv2
import numpy as np
import pyautogui
import time
import os
import sys
import traceback
from datetime import datetime, timedelta
import pytz
import platform
import io

# Настройка кодировки консоли
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

pyautogui.FAILSAFE = False


def load_templates():
    """Загрузка шаблонов изображений с корректными путями"""
    templates = {}
    try:
        # Определяем базовый путь в зависимости от окружения
        if getattr(sys, 'frozen', False):
            # Для EXE: путь к распакованным ресурсам
            base_dir = sys._MEIPASS
            resources_path = os.path.join(base_dir, 'resources', 'images', 'ImgLottery')
        else:
            # Для разработки: поднимаемся на 3 уровня выше от AntiAfkService
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            resources_path = os.path.join(base_dir, 'resources', 'images', 'ImgLottery')

        print(f"[DEBUG][lottery] Final resources path: {resources_path}")

        if not os.path.exists(resources_path):
            raise FileNotFoundError(f"Resources directory not found: {resources_path}")

        # Остальной код загрузки шаблонов без изменений
        template_files = {
            "Iconlottery": "Iconlottery.png",
            "Buttonlottery": "Buttonlottery.png",
            "Backspacetriggerlottery": "Backspacetriggerlottery.png",
            "Backspacetriggerlottery2": "Backspacetriggerlottery2.png"
        }

        for name, filename in template_files.items():
            full_path = os.path.join(resources_path, filename)
            img = cv2.imread(full_path, 0)
            if img is None:
                raise ValueError(f"Failed to load image: {full_path}")
            templates[name] = img

        return templates

    except Exception as e:
        print(f"[CRITICAL][lottery] Load templates failed: {str(e)}")
        traceback.print_exc()
        return None

def find_template(template, threshold=0.9):
    """Поиск шаблона с логированием"""
    try:
        print(f"[DEBUG][lottery] Searching for template ({template.shape[1]}x{template.shape[0]})...")
        screenshot = pyautogui.screenshot()
        gray_screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
        res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)

        if len(loc[0]) > 0:
            print(f"[DEBUG][lottery] Template found at {loc}")
            return loc
        else:
            print("[DEBUG][lottery] Template not found")
            return None

    except Exception as e:
        print(f"[ERROR][lottery] Template search failed: {str(e)}")
        traceback.print_exc()
        return None


def run_process(templates):
    """Основной процесс с детальным логированием"""
    try:
        print("[DEBUG][lottery] Starting main process...")
        pyautogui.press('up')
        print("[DEBUG][lottery] Sent UP key press")

        # Поиск Iconlottery
        print("[DEBUG][lottery] Searching for Iconlottery...")
        icon_found = False
        for attempt in range(5):
            loc = find_template(templates["Iconlottery"])
            if loc:
                y, x = loc[0][0], loc[1][0]
                center_x = x + templates["Iconlottery"].shape[1] // 2
                center_y = y + templates["Iconlottery"].shape[0] // 2
                print(f"[DEBUG][lottery] Clicking at ({center_x}, {center_y})")
                pyautogui.click(center_x, center_y)
                icon_found = True
                break
            print(f"[DEBUG][lottery] Iconlottery not found, attempt {attempt + 1}/5")
            time.sleep(1)

        if not icon_found:
            print("[ERROR][lottery] Failed to find Iconlottery")
            return False

        # Поиск Buttonlottery
        print("[DEBUG][lottery] Searching for Buttonlottery...")
        button_found = False
        for attempt in range(5):
            loc = find_template(templates["Buttonlottery"])
            if loc:
                y, x = loc[0][0], loc[1][0]
                center_x = x + templates["Buttonlottery"].shape[1] // 2
                center_y = y + templates["Buttonlottery"].shape[0] // 2
                print(f"[DEBUG][lottery] Clicking at ({center_x}, {center_y})")
                pyautogui.click(center_x, center_y)
                button_found = True
                break
            print(f"[DEBUG][lottery] Buttonlottery not found, attempt {attempt + 1}/5")
            time.sleep(1)

        if not button_found:
            print("[ERROR][lottery] Failed to find Buttonlottery")
            return False

        # Поиск триггеров Backspace
        print("[DEBUG][lottery] Starting backspace trigger monitoring...")
        start_time = time.time()
        while time.time() - start_time < 300:
            loc1 = find_template(templates["Backspacetriggerlottery"])
            loc2 = find_template(templates["Backspacetriggerlottery2"])

            if loc1 or loc2:
                print("[DEBUG][lottery] Trigger detected, pressing BACKSPACE")
                pyautogui.press('backspace', presses=2, interval=0.1)
                return True

            time.sleep(0.1)

        print("[WARNING][lottery] Backspace trigger timeout")
        return False

    except Exception as e:
        print(f"[CRITICAL][lottery] Process failed: {str(e)}")
        traceback.print_exc()
        return False


def run_lottery_service():
    """Главная функция сервиса с полным логированием"""
    print("[INFO][lottery] === SERVICE STARTING ===")
    print(f"[DEBUG][lottery] Platform: {platform.system()}")

    if platform.system() != "Windows":
        print("[CRITICAL][lottery] Windows required!")
        return

    print("[DEBUG][lottery] Initializing templates...")
    templates = load_templates()

    if not templates or len(templates) != 4:
        print("[CRITICAL][lottery] Missing templates, aborting")
        return

    print("[DEBUG][lottery] All templates loaded successfully")
    moscow_tz = pytz.timezone('Europe/Moscow')
    last_process_time = None

    try:
        print("[INFO][lottery] === SERVICE STARTED ===")
        while True:
            now = datetime.now(moscow_tz)
            print(f"[DEBUG][lottery] Current time: {now.strftime('%H:%M:%S')}")

            if 12 <= now.hour < 24:
                if last_process_time is None or (now - last_process_time) > timedelta(hours=2):
                    print("[DEBUG][lottery] Starting new process cycle...")
                    if run_process(templates):
                        last_process_time = now
                        print(f"[INFO][lottery] Process completed at {now.strftime('%H:%M:%S')}")
                    else:
                        print("[WARNING][lottery] Process failed, retrying in 5 minutes")
                        time.sleep(300)
                else:
                    next_run = last_process_time + timedelta(hours=2)
                    wait_time = (next_run - now).total_seconds()
                    print(f"[DEBUG][lottery] Next run at {next_run.strftime('%H:%M:%S')} ({wait_time:.0f}s remaining)")
                    time.sleep(30)
            else:
                print("[INFO][lottery] Outside working hours (12:00-23:59 MSK)")
                time.sleep(300)

    except KeyboardInterrupt:
        print("[INFO][lottery] Service stopped by user")
    except Exception as e:
        print(f"[CRITICAL][lottery] Service crashed: {str(e)}")
        traceback.print_exc()
    finally:
        print("[INFO][lottery] === SERVICE STOPPED ===")


if __name__ == "__main__":
    if "--service" in sys.argv:
        run_lottery_service()
    else:
        print("Для запуска сервиса используйте флаг --service")