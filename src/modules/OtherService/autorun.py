import time
import logging
import pydirectinput
import keyboard
import os
import json
import sys
from datetime import datetime


def run_autorun(
    settings_file="settings.json",
    autorun_key="+",
    log_file="autoran.txt",
):
    """
    Запускает процесс эмуляции зажатия клавиш 'w' и 'shift' при нажатии заданной клавиши.

    :param settings_file: Путь к файлу настроек.
    :param autorun_key: Клавиша для активации/деактивации эмуляции.
    :param log_file: Имя файла для логирования.
    """
    def log(message, level="info"):
        """Логирует сообщение с временной меткой."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        if level == "info":
            logging.info(log_message)
        elif level == "error":
            logging.error(log_message)

    def load_settings():
        """Загружает настройки из файла settings.json."""
        if os.path.exists(settings_file):
            try:
                with open(settings_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                log(f"Ошибка загрузки настроек: {e}", level="error")
        return {}

    # Определяем текущую папку (где лежит этот файл)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Если скрипт находится в src/modules/OtherService, то PROJECT_ROOT – это три уровня вверх
    project_root = os.path.abspath(os.path.join(base_dir, "..", "..", ".."))
    log(f"Используется корневая папка проекта: {project_root}")

    # Файл настроек находится в корневой папке проекта
    SETTINGS_FILE = os.path.join(project_root, settings_file)
    log(f"Используется файл настроек: {SETTINGS_FILE}")

    # Загружаем настройки и получаем клавишу для авторун (если не задано – по умолчанию '+')
    settings = load_settings()
    autorun_key = settings.get("autorun_key", autorun_key)
    log(f"Используется клавиша авторун: '{autorun_key}'")

    # Настройка логирования
    logs_dir = os.path.join(project_root, "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    LOG_FILE = os.path.join(logs_dir, log_file)

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    log("Запуск программы для эмуляции зажатия клавиш (autorun).")

    # Флаги состояния
    emulation_active = False   # Эмуляция клавиш не активна изначально
    key_pressed_flag = False   # Флаг для debounce

    # Главный цикл эмуляции
    try:
        while True:
            # Если нажата заданная клавиша и она ещё не была зафиксирована
            if keyboard.is_pressed(autorun_key):
                if not key_pressed_flag:
                    key_pressed_flag = True
                    # Переключаем состояние эмуляции
                    emulation_active = not emulation_active
                    if emulation_active:
                        log("Эмуляция активирована: зажимаем 'w' и 'shift'.")
                        pydirectinput.keyDown('w')
                        pydirectinput.keyDown('shift')
                    else:
                        log("Эмуляция деактивирована: отпускаем 'w' и 'shift'.")
                        pydirectinput.keyUp('w')
                        pydirectinput.keyUp('shift')
            else:
                key_pressed_flag = False  # Сбрасываем флаг, когда клавиша отпущена

            time.sleep(0.1)  # Небольшая задержка для стабильности работы
    except Exception as e:
        log(f"Произошла ошибка: {e}", level="error")
    finally:
        log("Завершение программы.")


if __name__ == "__main__":
    if "--service" in sys.argv:
        run_autorun()
    else:
        print("Флаг --service не передан, выход из программы.")