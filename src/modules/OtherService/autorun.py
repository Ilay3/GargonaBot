import time
import logging
import pydirectinput
import keyboard
import os
import json



# Определяем текущую папку (где лежит этот файл)
base_dir = os.path.dirname(os.path.abspath(__file__))
# Если скрипт находится в src/modules/OtherService, то PROJECT_ROOT – это три уровня вверх
project_root = os.path.abspath(os.path.join(base_dir, "..", "..", ".."))
print(f"Используется корневая папка проекта: {project_root}")

# Файл настроек находится в корневой папке проекта
SETTINGS_FILE = os.path.join(project_root, "settings.json")
print(f"Используется файл настроек: {SETTINGS_FILE}")

def load_settings():
    """Загружает настройки из файла settings.json."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
    return {}

# Загружаем настройки и получаем клавишу для авторун (если не задано – по умолчанию '+')
settings = load_settings()
autorun_key = settings.get("autorun_key", "+")
print(f"Используется клавиша авторун: '{autorun_key}'")

# Настройка логирования
logs_dir = os.path.join(project_root, "logs")
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)
LOG_FILE = os.path.join(logs_dir, "autoran.txt")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.info("Запуск программы для эмуляции зажатия клавиш (autorun).")

# Флаги состояния
emulation_active = False   # Эмуляция клавиш не активна изначально
key_pressed_flag = False   # Флаг для debounce

# Главный цикл эмуляции
while True:
    try:
        # Если нажата заданная клавиша и она ещё не была зафиксирована
        if keyboard.is_pressed(autorun_key):
            if not key_pressed_flag:
                key_pressed_flag = True
                # Переключаем состояние эмуляции
                emulation_active = not emulation_active
                if emulation_active:
                    logging.info("Эмуляция активирована: зажимаем 'w' и 'shift'.")
                    pydirectinput.keyDown('w')
                    pydirectinput.keyDown('shift')
                    print("Эмуляция включена: зажаты 'w' и 'shift'.")
                else:
                    logging.info("Эмуляция деактивирована: отпускаем 'w' и 'shift'.")
                    pydirectinput.keyUp('w')
                    pydirectinput.keyUp('shift')
                    print("Эмуляция отключена: отпущены 'w' и 'shift'.")
        else:
            key_pressed_flag = False  # Сбрасываем флаг, когда клавиша отпущена

        time.sleep(0.1)  # Небольшая задержка для стабильности работы
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        print(f"Произошла ошибка: {e}")
        break

logging.info("Завершение программы.")
