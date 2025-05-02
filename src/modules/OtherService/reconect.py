import json
import time
import pyautogui
import os
import cv2
import numpy as np
import easyocr
from datetime import datetime, time as dtime, timedelta
import pytz
import win32gui
import win32con
from ctypes import windll, c_int

pyautogui.FAILSAFE = False
SETTINGS_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'settings.json')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_PATH = os.path.join(BASE_DIR, '..', '..', '..', 'resources', 'images', 'ImgReconect')
reader = easyocr.Reader(['ru', 'en'])

def load_settings(path=SETTINGS_PATH):
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}

def save_settings(path, settings):
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(settings, file, indent=4, ensure_ascii=False)

def activate_window(window_part="Rage Multiplayer"):
    try:
        def callback(hwnd, hwnd_list):
            title = win32gui.GetWindowText(hwnd)
            if window_part.lower() in title.lower():
                hwnd_list.append(hwnd)
            return True

        hwnd_list = []
        win32gui.EnumWindows(callback, hwnd_list)
        if hwnd_list:
            hwnd = hwnd_list[0]
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            return True
        return False
    except Exception:
        return False

def find_text_easyocr(text, region=None):
    screenshot = pyautogui.screenshot(region=region)
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    results = reader.readtext(img, paragraph=False)
    for (bbox, word, confidence) in results:
        if text.lower() in word.lower():
            x_center = int((bbox[0][0] + bbox[2][0]) / 2)
            y_center = int((bbox[0][1] + bbox[2][1]) / 2)
            if region:
                x_center += region[0]
                y_center += region[1]
            return (x_center, y_center)
    return None

def try_find_and_click_text(text, max_attempts=15, offset=(0, 0), region=None):
    for _ in range(max_attempts):
        pos = find_text_easyocr(text, region)
        if pos:
            x, y = pos
            target_x = int(x + offset[0])
            target_y = int(y + offset[1])
            pyautogui.click(target_x, target_y)
            return True
        time.sleep(3)
    return False

def find_and_click(image_name, offset_x=0, offset_y=0, confidence=0.8):
    image_path = os.path.join(RESOURCES_PATH, image_name)
    if not os.path.exists(image_path):
        return False
    try:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        if location:
            x, y = location
            pyautogui.click(x + offset_x, y + offset_y)
            return True
        return False
    except Exception:
        return False

def process_spawn(spawn_type):
    spawn_images = {
        "Dom": ['dom.png'],
        "Kvartira": ['kvartira.png'],
        "Spawn": ['spawn.png'],
        "Lasttochka": ['lasttochka.png']
    }
    images = spawn_images.get(spawn_type, [])
    for img in images:
        if find_and_click(img, confidence=0.7):
            return True
    return False

def wait_for_correct_time():
    moscow_tz = pytz.timezone('Europe/Moscow')
    target = dtime(7, 30)
    now = datetime.now(moscow_tz)
    if now.time() >= target:
        tomorrow = now.date() + timedelta(days=1)
        target_dt = moscow_tz.localize(datetime.combine(tomorrow, target))
    else:
        target_dt = moscow_tz.localize(datetime.combine(now.date(), target))
    while datetime.now(moscow_tz) < target_dt:
        time.sleep(60)

def run_script(settings, wait_until_710=False):
    if wait_until_710:
        wait_for_correct_time()

    if 'password' not in settings or not settings['password']:
        raise ValueError("Пароль не задан")
    if 'character' not in settings or settings['character'] not in ["First", "Second", "Third"]:
        raise ValueError("Некорректный персонаж")
    if 'spawn' not in settings or settings['spawn'] not in ["Dom", "Kvartira", "Spawn", "Lasttochka"]:
        raise ValueError("Некорректная точка спавна")

    try:
        windll.shcore.SetProcessDpiAwareness(c_int(2))
    except Exception:
        pass

    pyautogui.press('f1')
    time.sleep(1)
    find_and_click('image1.png')
    time.sleep(1)
    find_and_click('image2.png')
    time.sleep(1)

    activate_window()
    if not try_find_and_click_text("Пароль", offset=(30, 0), region=(0, 0, 1920, 1080)):
        return

    pyautogui.write(settings['password'])
    time.sleep(1)

    if not try_find_and_click_text("Войти", region=(0, 0, 1920, 1080)):
        return

    time.sleep(4)
    character_positions = {
        "First": (1565, 368),
        "Second": (1565, 526),
        "Third": (1565, 695)
    }
    if settings['character'] in character_positions:
        x, y = character_positions[settings['character']]
        pyautogui.click(x, y)
        time.sleep(2)

    find_and_click('image4.png', confidence=0.7)
    process_spawn(settings['spawn'])
    find_and_click('image7.png', confidence=0.7)

if __name__ == "__main__":
    settings = load_settings()
    run_script(settings, wait_until_710=True)