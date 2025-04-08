import os
import sys
import cv2
import numpy as np
import pyautogui
import time
import keyboard
import argparse
from datetime import datetime
import io
import traceback
def get_resource_path(relative_path):
    """Возвращает абсолютный путь к ресурсу, работает для dev и для PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        # Если запущено из .exe, используем временную папку
        base_path = sys._MEIPASS
    else:
        # Если запущено из скрипта, используем текущую директорию
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
# Безопасная установка кодировки только если stdout/stderr существуют
try:
    if sys.stdout and hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if sys.stderr and hasattr(sys.stderr, "buffer"):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
except Exception:
    pass  # Безопасно игнорируем в случае запуска из .exe с --noconsole

def log(message, level="INFO"):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    log_message = f"[{timestamp}] [{level}] {message}"
    print(log_message)
    with open("cookbot.log", "a", encoding='utf-8', errors='replace') as f:
        f.write(log_message + "\n")

def debug_screenshot(screenshot, name):
    debug_dir = "debug_cook"
    os.makedirs(debug_dir, exist_ok=True)
    cv2.imwrite(os.path.join(debug_dir, f"{name}_{datetime.now().strftime('%H%M%S%f')}.png"), screenshot)

def run_cookbot(
        vegetables_path=get_resource_path("resources/images/ImgCook/Vegetables.png"),
        knife_path=get_resource_path("resources/images/ImgCook/Knife.png"),
        water_path=get_resource_path("resources/images/ImgCook/Water.png"),
        venchik_path=get_resource_path("resources/images/ImgCook/Venchik.png"),
        meat_path=get_resource_path("resources/images/ImgCook/Meat.png"),
        fire_path=get_resource_path("resources/images/ImgCook/Fire.png"),
        start_cook_path=get_resource_path("resources/images/ImgCook/StartCook.png"),
        threshold=0.9
):


    try:
        log("Инициализация CookBot")
        pyautogui.FAILSAFE = False

        # Парсинг аргументов
        parser = argparse.ArgumentParser()
        parser.add_argument("--service", type=str, required=False, default="cookbot")
        parser.add_argument("--dish", type=str, required=True)
        parser.add_argument("--quantity", type=int, required=True)
        args = parser.parse_args()

        log(f"Получены параметры: сервис={args.service}, блюдо={args.dish}, количество={args.quantity}")

        # Преобразование путей
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log(f"Директория скрипта: {script_dir}")

        # Абсолютные пути
        path_vars = {
            "Vegetables": vegetables_path,
            "Knife": knife_path,
            "Water": water_path,
            "Venchik": venchik_path,
            "Meat": meat_path,
            "Fire": fire_path,
            "StartCook": start_cook_path,
        }

        paths = {name: os.path.abspath(os.path.join(script_dir, rel_path)) for name, rel_path in path_vars.items()}

        # Логирование путей
        for name, path in paths.items():
            rel_path = path_vars[name]
            log(f"Обработка {name}:")
            log(f"  Относительный путь: {rel_path}")
            log(f"  Абсолютный путь: {path}")
            log(f"  Файл существует: {os.path.exists(path)}")
            log(f"  Размер файла: {os.path.getsize(path) if os.path.exists(path) else 0} байт")

        # Загрузка шаблонов
        templates = {}
        for name, path in paths.items():
            template = cv2.imread(path, 0)
            if template is None:
                log(f"Не удалось загрузить {name}", "ERROR")
                return
            templates[name] = template
            log(f"Успешно загружен {name} (размер: {template.shape[1]}x{template.shape[0]})")

        # Конфигурация рецептов
        menu_config = {
            "Салат": ["Vegetables", "Knife", "StartCook"],
            "Смузи": ["Vegetables", "Water", "Venchik", "StartCook"],
            "Рагу": ["Meat", "Water", "Vegetables", "Fire", "StartCook"]
        }

        move_positions = {
            "Салат": {"Vegetables": (684, 289), "Knife": (811, 298), "StartCook": (812, 671)},
            "Смузи": {"Vegetables": (684, 289), "Water": (811, 298), "Venchik": (930, 299), "StartCook": (812, 671)},
            "Рагу": {"Meat": (930, 299), "Water": (811, 298), "Vegetables": (684, 289), "Fire": (672, 419),
                     "StartCook": (812, 671)}
        }

        if args.dish not in menu_config:
            log(f"Неизвестное блюдо: {args.dish}", "ERROR")
            return

        log(f"Конфигурация для {args.dish}:")
        log(f"  Шаги: {menu_config[args.dish]}")
        log(f"  Позиции: {move_positions[args.dish]}")

        log(f"Начало приготовления {args.quantity} порций {args.dish}")

        for i in range(args.quantity):
            if keyboard.is_pressed('0'):
                log("Остановка по клавише 0")
                return

            log(f"Приготовление порции {i + 1}/{args.quantity}")

            for step in menu_config[args.dish]:
                log(f"Обработка шага: {step}")
                template = templates[step]

                attempts = 0
                while True:
                    if keyboard.is_pressed('0'):
                        log("Остановка по клавише 0")
                        return

                    screenshot = pyautogui.screenshot()
                    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                    gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)

                    res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, max_loc = cv2.minMaxLoc(res)

                    log(f"Поиск {step}: макс. совпадение={max_val:.2f}, порог={threshold}")

                    if max_val >= threshold:
                        x = max_loc[0] + template.shape[1] // 2
                        y = max_loc[1] + template.shape[0] // 2
                        log(f"Найдено {step} @ ({x},{y}) (совпадение={max_val:.2f})")

                        if step in move_positions[args.dish]:
                            new_x, new_y = move_positions[args.dish][step]
                            log(f"Перемещение {step} в ({new_x},{new_y})")
                            pyautogui.moveTo(x, y, duration=0.3)
                            pyautogui.dragTo(new_x, new_y, duration=0.5, button='left')

                        log(f"Клик по {step} @ ({x},{y})")
                        pyautogui.click(x, y)
                        break
                    else:
                        attempts += 1
                        if attempts > 10:
                            log(f"Не найдено {step} после 10 попыток", "ERROR")
                            debug_screenshot(gray, f"missed_{step}")
                            return
                        time.sleep(0.5)

                time.sleep(0.5)

            log(f"Порция {i + 1} завершена")
            time.sleep(8)

        log("Все блюда успешно приготовлены!")

    except Exception as e:
        log(f"Критическая ошибка: {str(e)}", "ERROR")
        log(traceback.format_exc(), "ERROR")

if __name__ == "__main__":
    if "--service=cookbot" in sys.argv:
        run_cookbot()
    else:
        print("Используйте --service=cookbot для запуска")
