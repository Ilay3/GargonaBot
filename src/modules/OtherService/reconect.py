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
# Изменим путь на относительный от корня проекта
SETTINGS_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'settings.json')
# В начале скрипта добавить
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_PATH = os.path.join(BASE_DIR, '..', '..', '..', 'resources', 'images', 'ImgReconect')
reader = easyocr.Reader(['ru', 'en'])  # Инициализация OCR


def load_settings(path=SETTINGS_PATH):
    # Нормализуем путь и показываем относительный путь
    relative_path = os.path.relpath(path, start=os.getcwd())
    print(f"Проверяю наличие настроек по относительному пути: {relative_path}")

    if not os.path.exists(path):
        print(f"Файл settings.json не найден. Создаю новый по пути: {relative_path}")
        return {}

    with open(path, 'r', encoding='utf-8') as file:
        try:
            settings = json.load(file)
            print(f"Настройки успешно загружены из: {relative_path}")
            return settings
        except json.JSONDecodeError:
            print(f"Ошибка: Некорректный формат файла в {relative_path}. Создаю новый.")
            return {}

def save_settings(path, settings):
    relative_path = os.path.relpath(path, start=os.getcwd())
    print(f"Сохраняю настройки по относительному пути: {relative_path}")
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
            print(f"Активировано окно: {win32gui.GetWindowText(hwnd)}")
            return True
        return False
    except Exception as e:
        print(f"Ошибка активации окна: {str(e)}")
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


def try_find_and_click_text(text, max_attempts=10, offset=(0, 0), region=None):
    for attempt in range(1, max_attempts + 1):
        print(f"Попытка {attempt} найти текст '{text}'")
        pos = find_text_easyocr(text, region)
        if pos:
            x, y = pos
            target_x = int(x + offset[0])
            target_y = int(y + offset[1])
            pyautogui.click(target_x, target_y)
            print(f"Найден текст '{text}' и кликнут")
            return True
        time.sleep(3)
    print(f"Текст '{text}' не найден после {max_attempts} попыток")
    return False


def find_and_click(image_name, offset_x=0, offset_y=0, confidence=0.8):
    image_path = os.path.join(RESOURCES_PATH, image_name)
    print(f"Ищу изображение по пути: {image_path}")  # Добавить логирование

    if not os.path.exists(image_path):
        print(f"ОШИБКА: Файл {image_path} не существует!")
        return False

    try:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        if location:
            x, y = location
            pyautogui.click(x + offset_x, y + offset_y)
            print(f"Изображение {image_name} найдено и кликнуто.")
            return True
        return False
    except Exception as e:
        print(f"Ошибка поиска изображения: {str(e)}")
        return False


def process_spawn(spawn_type):
    spawn_images = {
        "Dom": ['dom.png'],
        "Kvartira": ['kvartira.png'],
        "Spawn": ['spawn.png'],
        "Lasttochka": ['lasttochka.png']
    }
    images = spawn_images.get(spawn_type, [])
    print(f"Ищу точку спавна {spawn_type} по изображениям: {images}")
    for img in images:
        if find_and_click(img, confidence=0.7):
            print(f"Точка спавна {spawn_type} найдена по изображению {img}")
            return True
    print(f"Все изображения для {spawn_type} не найдены")
    return False


def wait_for_correct_time():
    moscow_tz = pytz.timezone('Europe/Moscow')
    target = dtime(21, 22)
    now = datetime.now(moscow_tz)
    if now.time() >= target:
        tomorrow = now.date() + timedelta(days=1)
        target_dt = moscow_tz.localize(datetime.combine(tomorrow, target))
    else:
        target_dt = moscow_tz.localize(datetime.combine(now.date(), target))
    while datetime.now(moscow_tz) < target_dt:
        current = datetime.now(moscow_tz)
        print(f"Текущее время: {current.strftime('%H:%M')}. Ожидаю {target_dt.strftime('%H:%M')}...")
        time.sleep(60)
    print(f"Время {target_dt.strftime('%H:%M')}! Начинаю выполнение скрипта.")


def run_script(settings, wait_until_710=False):
    if wait_until_710:
        wait_for_correct_time()

    if 'password' not in settings or not settings['password']:
        raise ValueError("Пароль не задан в настройках.")
    if 'character' not in settings or settings['character'] not in ["First", "Second", "Third"]:
        raise ValueError("Некорректное значение персонажа.")
    if 'spawn' not in settings or settings['spawn'] not in ["Dom", "Kvartira", "Spawn", "Lasttochka"]:
        raise ValueError("Некорректное значение точки спауна.")

    try:
        windll.shcore.SetProcessDpiAwareness(c_int(2))
    except Exception as e:
        print(f"Ошибка настройки DPI: {str(e)}")

    pyautogui.press('f1')
    time.sleep(1)

    find_and_click('image1.png')
    time.sleep(1)

    find_and_click('image2.png')
    time.sleep(1)



    # Новый функционал из второго кода
    activate_window()
    if not try_find_and_click_text("Пароль", offset=(30, 0), region=(0, 0, 1920, 1080)):
        print("Ошибка: Поле для пароля не найдено")
        return

    pyautogui.write(settings['password'])
    time.sleep(1)

    if not try_find_and_click_text("Войти", region=(0, 0, 1920, 1080)):
        print("Ошибка: Кнопка входа не найдена")
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
    else:
        print("Ошибка: Некорректный персонаж")

    if not find_and_click('image4.png', confidence=0.7):
        print("Ошибка: image4 не найдена")

    if not process_spawn(settings['spawn']):
        print(f"Ошибка: не удалось найти точку спавна {settings['spawn']}")
        return



    if not find_and_click('image7.png', confidence=0.7):
        print("Ошибка: image7 не найдена")


if __name__ == "__main__":
    settings = load_settings()
    wait_until_710 = True
    print("Ожидаю 7:10 утра...")
    run_script(settings, wait_until_710)