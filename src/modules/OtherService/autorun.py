import time
import pydirectinput
import keyboard
import os
import json
import sys
import platform

def run_autorun(settings_file="settings.json"):
    """
    Запускает процесс эмуляции зажатия клавиш 'w' и 'shift' при нажатии заданной клавиши.
    """
    def load_settings():
        """Загружает настройки из файла settings.json."""
        if os.path.exists(settings_file):
            try:
                with open(settings_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    # Проверяем ОС
    current_os = platform.system()
    if current_os != "Windows":
        return

    # Загружаем настройки
    settings = load_settings()
    autorun_key = settings.get("autorun_key", "+")

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
                        try:
                            pydirectinput.keyDown('w')
                            pydirectinput.keyDown('shift')
                        except Exception:
                            emulation_active = False
                    else:
                        try:
                            pydirectinput.keyUp('w')
                            pydirectinput.keyUp('shift')
                        except Exception:
                            pass
            else:
                key_pressed_flag = False

            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    except Exception:
        pass
    finally:
        try:
            pydirectinput.keyUp('w')
            pydirectinput.keyUp('shift')
        except:
            pass

if __name__ == "__main__":
    if "--service" in sys.argv:
        run_autorun()