import os
import sys
import json
import time
import pyautogui
import argparse
import traceback
import requests
from datetime import datetime
import pytz
import win32gui
import win32con
from ctypes import windll, c_int

# ===================================================
# 0. Настройки DPI и прав администратора
# ===================================================
try:
    windll.shcore.SetProcessDpiAwareness(c_int(2))
except Exception as e:
    print(f"[WARNING] Ошибка настройки DPI: {str(e)}")

# ===================================================
# 1. Настройка путей и импорта
# ===================================================

project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(project_root)
print(f"[DEBUG] Добавлен путь к проекту: {project_root}")

try:
    from main import send_screenshot_to_telegram
    from modules.ProcessChecker import process_checker
    print("[DEBUG] Модули успешно импортированы")
except ImportError as e:
    print(f"[ERROR] Ошибка импорта: {str(e)}")
    raise

# ===================================================
# 2. Конфигурация путей
# ===================================================

def get_images_base_dir():
    # Определяем базовый путь в зависимости от того, скомпилирован код или нет
    if getattr(sys, 'frozen', False):
        # Режим исполнения после компиляции (EXE)
        base_dir = os.path.join(sys._MEIPASS, 'resources', 'images', 'ImgFullReconect')
    else:
        # Режим разработки (исходный код)
        base_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..", "..", "..",
                "resources",
                "images",
                "ImgFullReconect"
            )
        )

    print(f"[DEBUG] Путь к изображениям: {base_dir}")
    if not os.path.exists(base_dir):
        raise FileNotFoundError(f"[ERROR] Папка с изображениями не найдена: {base_dir}")
    return base_dir

IMAGES_BASE_DIR = get_images_base_dir()

# ===================================================
# 3. Основные функции
# ===================================================

pyautogui.FAILSAFE = False

def try_find_and_click(image_name, max_attempts=10, confidence=0.8, offset=(0, 0), region=None):
    """Пытается найти и кликнуть по изображению до max_attempts раз."""
    print(f"[DEBUG] Поиск изображения {image_name} (макс. попыток: {max_attempts})")
    image_path = get_image_path(image_name)

    for attempt in range(1, max_attempts + 1):
        print(f"[DEBUG] Попытка {attempt} для {image_name}")
        activate_window()
        try:
            pos = pyautogui.locateCenterOnScreen(
                image_path,
                confidence=confidence,
                grayscale=False,
                region=region
            )
            if pos:
                x, y = pos
                target_x = int(x + offset[0])
                target_y = int(y + offset[1])
                pyautogui.click(target_x, target_y)
                print(f"[SUCCESS] Найдено и кликнуто: {image_name}")
                return True
        except pyautogui.ImageNotFoundException:
            print(f"[DEBUG] Изображение {image_name} не найдено, попытка {attempt}")
        except Exception as e:
            print(f"[ERROR] Ошибка при поиске {image_name}: {str(e)}")
        time.sleep(3)

    print(f"[WARNING] Изображение {image_name} не найдено после {max_attempts} попыток")
    return False

def process_spawn(spawn_type):
    spawn_images = {
        "Dom": ['dom.png'],
        "Kvartira": ['kvartira.png'],
        "Spawn": ['spawn.png'],
        "Lasttochka": ['lasttochka.png']
    }

    images = spawn_images.get(spawn_type, [])
    if not images:
        print(f"[ERROR] Неизвестный тип спауна: {spawn_type}")
        return False

    print(f"[INFO] Обработка спауна: {spawn_type}")
    for img in images:
        if try_find_and_click(img, max_attempts=15, confidence=0.7):
            return True
    return False


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
            print(f"[OK] Активировано окно: {win32gui.GetWindowText(hwnd)}")
            return True

        print(f"[WARNING] Окно содержащее '{window_part}' не найдено")
        return False
    except Exception as e:
        print(f"[ERROR] Ошибка активации окна: {str(e)}")
        return False

def get_image_path(image_name):
    image_path = os.path.join(IMAGES_BASE_DIR, image_name)
    print(f"[DEBUG] Проверка изображения: {image_path}")
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"[ERROR] Изображение отсутствует: {image_path}")
    return image_path

def check_resources():
    print("[DEBUG] Начало проверки ресурсов")
    required_images = [
        "image1.png", "image21.png", "image6.png",
        "image3.png", "image5.png", "image4.png",
        "image7.png", "imagevyhod.png",
        "dom.png", "kvartira.png", "spawn.png", "lasttochka.png"
    ]

    missing = []
    for img in required_images:
        try:
            get_image_path(img)
            print(f"[DEBUG] Изображение найдено: {img}")
        except FileNotFoundError:
            missing.append(img)
            print(f"[ERROR] Изображение отсутствует: {img}")

    if missing:
        error_msg = "[CRITICAL] Отсутствуют изображения:\n- " + "\n- ".join(missing)
        print(error_msg)
        raise RuntimeError(error_msg)
    print("[DEBUG] Все ресурсы проверены")

def find_and_click(image_name, confidence=0.8, offset=(0, 0), region=None):
    """Бесконечный поиск изображения до успешного клика"""
    print(f"[DEBUG] Начало поиска изображения: {image_name}")
    try:
        image_path = get_image_path(image_name)
        attempt = 1

        while True:
            activate_window()
            print(f"[DEBUG] Попытка {attempt} для {image_name}")

            try:
                pos = pyautogui.locateCenterOnScreen(
                    image_path,
                    confidence=confidence,
                    grayscale=False,
                    region=region
                )

                if pos:
                    x, y = pos
                    target_x = int(x + offset[0])
                    target_y = int(y + offset[1])

                    print(f"[SUCCESS] Найдено: {image_name} | Координаты: ({target_x},{target_y})")
                    pyautogui.click(target_x, target_y)
                    print("[DEBUG] Клик успешно выполнен")
                    time.sleep(1)
                    return True

                print(f"[DEBUG] Изображение {image_name} не найдено, повторная попытка...")
                time.sleep(3)
                attempt += 1

            except pyautogui.ImageNotFoundException:
                print(f"[DEBUG] Изображение {image_name} не найдено, повторная попытка...")
                time.sleep(3)
                attempt += 1
                continue

    except Exception as e:
        print(f"[CRITICAL] Ошибка в find_and_click: {str(e)}")
        print(traceback.format_exc())
        return False

def load_settings(settings_path):
    print(f"[DEBUG] Загрузка настроек из: {settings_path}")
    default_settings = {
        "password": "",
        "character": "First",
        "spawn": "",
        "rage_mp_path": ""
    }

    try:
        if not os.path.exists(settings_path):
            raise FileNotFoundError(f"[ERROR] Файл настроек не найден: {settings_path}")

        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
            print("[DEBUG] Содержимое файла настроек:")
            print(json.dumps(settings, indent=4, ensure_ascii=False))

        for key in default_settings:
            if key not in settings or not settings[key]:
                if key in ["character", "spawn"]:
                    settings[key] = default_settings[key]
                    continue
                raise ValueError(f"[ERROR] Не заполнено поле: {key}")

        return settings

    except Exception as e:
        print(f"[ERROR] Ошибка загрузки настроек: {str(e)}")
        print("[INFO] Создание нового файла...")

        settings = default_settings.copy()
        for key in settings:
            settings[key] = input(f"Введите значение для {key}: ")

        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)

        return settings

# ===================================================
# 4. Основная логика
# ===================================================

def run_fullreconnect_bot():
    try:
        try:
            is_admin = windll.shell32.IsUserAnAdmin() != 0
            if not is_admin:
                print("[CRITICAL] ТРЕБУЮТСЯ ПРАВА АДМИНИСТРАТОРА! Запустите скрипт от имени администратора")
                return
        except Exception as e:
            print(f"[ERROR] Ошибка проверки прав: {str(e)}")

        print("[DEBUG] [FULLRECONNECT] Начало выполнения полного реконнекта")
        activate_window()

        try:
            from screeninfo import get_monitors
            for m in get_monitors():
                scale_factor = 1.0
                if hasattr(m, 'scale'):
                    scale_factor = m.scale
                elif hasattr(m, 'width_physical') and m.width_physical > 0:
                    scale_factor = m.width / m.width_physical

                print(f"[DEBUG] Монитор: {m.width}x{m.height} | Масштаб: {scale_factor:.1f}")
                if scale_factor != 1.0:
                    print("[WARNING] Обнаружено масштабирование экрана!")
        except Exception as e:
            print(f"[ERROR] Ошибка проверки монитора: {str(e)}")

        CONFIG = {
            "image_sequence": [
                ("image1.png", 0, 0, 1),
                ("image21.png", 0, 0, 1),
                ("image6.png", 0, 0, 1),
                ("image3.png", 30, 0, 1),
                ("image5.png", 0, 0, 1),
                ("image4.png", 0, 0, 1)
            ],
            "exit_image": "imagevyhod.png"
        }

        character_positions = {
            "First": (1565, 368),
            "Second": (1565, 526),
            "Third": (1565, 695)
        }

        parser = argparse.ArgumentParser()
        parser.add_argument("--service", type=str, default="reconnect")
        parser.add_argument(
            "--settings",
            type=str,
            default=os.path.join(os.environ["TEMP"], "settings.json"),
            help="Path to settings file"
        )
        args = parser.parse_args()

        settings = load_settings(args.settings)

        print("[DEBUG] [FULLRECONNECT] Проверка активности игры...")
        if process_checker.is_game_active():
            print("[INFO] Игра запущена. Выполняем перезаход...")
            activate_window()

            pyautogui.press('f1')
            time.sleep(2)

            if not find_and_click(CONFIG["exit_image"]):
                print("[ERROR] Не удалось найти кнопку выхода")
                return
            time.sleep(5)

        rage_mp_path = settings["rage_mp_path"]
        if os.path.exists(rage_mp_path):
            try:
                print("[INFO] Запуск RageMP...")
                os.startfile(rage_mp_path, "runas")
                time.sleep(15)
            except Exception as e:
                print(f"[ERROR] Ошибка при запуске RageMP: {str(e)}")
                return
        else:
            print(f"[ERROR] Путь к RageMP не существует: {rage_mp_path}")
            return

        # Основной цикл обработки
        spawn_failed = False
        last_processed_step = -1

        for idx, (image, offset_x, offset_y, required) in enumerate(CONFIG["image_sequence"]):
            if spawn_failed:
                continue

            activate_window()
            print(f"[INFO] Обработка шага {idx + 1}/{len(CONFIG['image_sequence'])}: {image}")

            if image == "image4.png":
                print("[DEBUG] Поиск image4 с расширенными параметрами")
                success = try_find_and_click(
                    image,
                    confidence=0.7,
                    offset=(offset_x, offset_y),
                )
                if not success:
                    print("[CRITICAL] Не удалось найти image4!")
                    spawn_failed = True
                    last_processed_step = idx
                    break
                continue

            find_and_click(image, offset=(offset_x, offset_y))

            if image == "image3.png":
                print("[ACTION] Ввод пароля...")
                pyautogui.write(settings["password"])
                time.sleep(1)

            if image == "image5.png":
                print("[ACTION] Выбор персонажа...")
                time.sleep(3)

                selected_character = settings.get("character", "First")
                target_pos = character_positions.get(selected_character)

                if not target_pos:
                    print(f"[ERROR] Неизвестный персонаж: {selected_character}, используется First")
                    target_pos = character_positions["First"]

                print(f"[ACTION] Клик по позиции {selected_character}: {target_pos}")
                pyautogui.click(target_pos)
                time.sleep(1)
                print("[INFO] Ожидание загрузки интерфейса...")
                time.sleep(5)

                print("[INFO] Дополнительное ожидание перед поиском спауна")
                time.sleep(5)

            last_processed_step = idx

        # Попытка выбрать точку спауна по настройке
        spawn_type = settings.get("spawn")
        spawn_failed = False

        if spawn_type:
            print(f"[INFO] Поиск спауна: {spawn_type}")
            spawn_success = process_spawn(spawn_type)
            if not spawn_success:
                print("[ERROR] Не удалось найти точку спауна по изображению")
                spawn_failed = True
        else:
            print("[INFO] Тип спауна не указан, выбор спауна пропущен")

        # Попытка найти и нажать image7 (подтверждение спауна)
        if not spawn_failed:
            print("[INFO] Поиск и нажатие image7 (подтверждение)")
            found_image7 = try_find_and_click("image7.png", max_attempts=15, confidence=0.7)
            if not found_image7:
                print("[ERROR] Картинка image7 не найдена")
                spawn_failed = True
        else:
            print("[ERROR] Не удалось выполнить спаун, пропускаем подтверждение image7")

        # Создание скриншота и отправка результата
        try:
            screenshot_dir = os.path.join(project_root, "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            timestamp = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y%m%d_%H%M%S')

            if spawn_failed:
                screenshot_path = os.path.join(screenshot_dir, f"error_{timestamp}.png")
                message = "Успешное подключение"
            else:
                print("[INFO] Ожидание завершения загрузки...")
                time.sleep(10)
                screenshot_path = os.path.join(screenshot_dir, f"success_{timestamp}.png")
                message = "Успешное подключение"

            pyautogui.screenshot(screenshot_path)
            print(f"[INFO] Скриншот сохранен: {screenshot_path}")

            if send_screenshot_to_telegram(screenshot_path, message):
                os.remove(screenshot_path)
                print("[INFO] Скриншот отправлен и удален")
            else:
                print("[ERROR] Не удалось отправить скриншот")

        except Exception as e:
            print(f"[ERROR] Ошибка при работе со скриншотом: {str(e)}")

        if spawn_failed:
            print("[SUCCESS] Полный перезаход выполнен успешно, без выбора спауна!")
            return

        print("[SUCCESS] Полный перезаход выполнен успешно!")

    except Exception as e:
        print(f"[CRITICAL] Критическая ошибка: {str(e)}")
        print(traceback.format_exc())

if __name__ == "__main__":
    check_resources()
    run_fullreconnect_bot()