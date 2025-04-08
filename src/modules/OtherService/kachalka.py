import time
import keyboard
from mss import mss
import numpy as np
import sys
import os
import json
from datetime import datetime


def get_resource_path(relative_path):
    """Возвращает абсолютный путь к ресурсу, работает для dev и для PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def run_kachalka(
        settings_file=get_resource_path("settings.json"),
):
    print("Функция run_kachalka запущена.")



    def load_settings():
        """Загружает настройки из файла settings.json."""
        default_settings = {
            "monitor": {"left": 767, "top": 585, "width": 469, "height": 345},
            "color_ranges": [
                [100, 150, 240, 260, 140, 180],
                [180, 220, 240, 260, 170, 210]
            ],
            "step": 2,
            "press_key": "space"
        }

        if os.path.exists(settings_file):
            try:
                with open(settings_file, "r") as f:
                    loaded = json.load(f)
                    return {**default_settings, **loaded}
            except Exception as e:
                print(f"Ошибка загрузки настроек: {e}")
                return default_settings
        return default_settings

    def get_screen(monitor):
        try:
            with mss() as sct:
                screenshot = sct.grab(monitor)
                return np.array(screenshot)
        except Exception as e:
            print(f"Ошибка захвата экрана: {e}")
            return None

    def check_colors(screen, color_ranges, step):
        if screen is None:
            return False

        pixels = screen[::step, ::step]

        for rmin, rmax, gmin, gmax, bmin, bmax in color_ranges:
            r_mask = (pixels[:, :, 0] >= rmin) & (pixels[:, :, 0] <= rmax)
            g_mask = (pixels[:, :, 1] >= gmin) & (pixels[:, :, 1] <= gmax)
            b_mask = (pixels[:, :, 2] >= bmin) & (pixels[:, :, 2] <= bmax)

            if np.any(r_mask & g_mask & b_mask):
                return True
        return False

    # Загрузка настроек
    settings = load_settings()
    monitor = settings["monitor"]
    color_ranges = settings["color_ranges"]
    step = settings["step"]
    press_key = settings["press_key"]

    print(f"Настройки загружены: {settings}")

    print("Сервис запущен...")
    try:


        while True:
            screen = get_screen(monitor)
            if check_colors(screen, color_ranges, step):
                time.sleep(0.1)
                keyboard.press_and_release(press_key)
                print(f"Нажатие клавиши {press_key}")
                time.sleep(0.1)

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nБот остановлен")
    except Exception as e:
        print(f"Критическая ошибка: {e}")


if __name__ == "__main__":
    if "--service=kachalka" in sys.argv:
        run_kachalka()
    else:
        print("Флаг --service=kachalka не передан, выход из программы.")