import time
import logging
import pydirectinput
import keyboard
import os
import json
import sys
from datetime import datetime
import platform


def run_autorun(
    settings_file="settings.json",
    autorun_key="+",
    log_file="autoran.txt",
):
    """
    Запускает процесс эмуляции зажатия клавиш 'w' и 'shift' при нажатии заданной клавиши.
    Учитывает возможные проблемы с окружением и библиотеками.
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

    # Проверяем ОС
    current_os = platform.system()
    if current_os != "Windows":
        log(f"Ошибка: Скрипт поддерживает только Windows. Текущая ОС: {current_os}", level="error")
        return

    # Определяем текущую папку (где лежит этот файл)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_dir, "..", "..", ".."))
    log(f"Используется корневая папка проекта: {project_root}")

    # Файл настроек
    SETTINGS_FILE = os.path.join(project_root, settings_file)
    log(f"Используется файл настроек: {SETTINGS_FILE}")

    # Загружаем настройки
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
    emulation_active = False
    key_pressed_flag = False

    # Главный цикл эмуляции
    try:
        while True:
            if keyboard.is_pressed(autorun_key):
                if not key_pressed_flag:
                    key_pressed_flag = True
                    emulation_active = not emulation_active
                    if emulation_active:
                        log("Эмуляция активирована: зажимаем 'w' и 'shift'.")
                        try:
                            pydirectinput.keyDown('w')
                            pydirectinput.keyDown('shift')
                        except Exception as e:
                            log(f"Ошибка эмуляции: {e}", level="error")
                            emulation_active = False  # Сбрасываем флаг при ошибке
                    else:
                        log("Эмуляция деактивирована: отпускаем 'w' и 'shift'.")
                        try:
                            pydirectinput.keyUp('w')
                            pydirectinput.keyUp('shift')
                        except Exception as e:
                            log(f"Ошибка при отпускании клавиш: {e}", level="error")
            else:
                key_pressed_flag = False

            time.sleep(0.1)
    except KeyboardInterrupt:
        log("Программа остановлена пользователем.")
    except Exception as e:
        log(f"Критическая ошибка: {e}", level="error")
    finally:
        # Гарантированно отпускаем клавиши при завершении
        try:
            pydirectinput.keyUp('w')
            pydirectinput.keyUp('shift')
        except:
            pass
        log("Завершение программы.")


if __name__ == "__main__":
    if "--service" in sys.argv:
        run_autorun()
    else:
        print("Флаг --service не передан, выход из программы.")