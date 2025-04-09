import cv2
import numpy as np
import pyautogui
import time
import sys
import os
from datetime import datetime
import io


def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_path, relative_path)
    return full_path.replace('\\', os.sep) if os.sep == '/' else full_path.replace('/', os.sep)


try:
    if sys.stdout and hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if sys.stderr and hasattr(sys.stderr, "buffer"):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
except Exception:
    pass


def run_taxi(
        kpk_path=get_resource_path("resources/images/ImgTaxi/KPK.png"),
        taxi_accept_path=get_resource_path("resources/images/ImgTaxi/taxiAccept.png"),
        zakazgotov_path=get_resource_path("resources/images/ImgTaxi/zakazgotov.png"),
        restart_trigger_path=get_resource_path("resources/images/ImgTaxi/RestartTrigger.png"),
        threshold=0.8
):
    print("[TAXI][INIT] Инициализация такси-бота")

    def log(message, level="INFO"):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[TAXI][{timestamp}][{level}] {message}")

    try:
        paths = {
            "KPK": kpk_path,
            "TaxiAccept": taxi_accept_path,
            "ZakazGotov": zakazgotov_path,
            "RestartTrigger": restart_trigger_path
        }

        for name, path in paths.items():
            if not os.path.exists(path):
                log(f"Файл {name} не найден: {path}", "ERROR")
                return
            log(f"Ресурс {name} валиден", "DEBUG")

        templates = {}
        for name, path in paths.items():
            template = cv2.imread(path, 0)
            if template is None:
                log(f"Ошибка загрузки {name}", "CRITICAL")
                return
            templates[name] = template

        pyautogui.FAILSAFE = False
        log("Инициализация завершена", "SUCCESS")

        def enhanced_find_template(template_name, cycle_num, attempt_num):
            try:
                screenshot = pyautogui.screenshot()
                img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                res = cv2.matchTemplate(gray, templates[template_name], cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(res)

                if max_val >= threshold:
                    w, h = templates[template_name].shape[::-1]
                    top_left = max_loc
                    center = (top_left[0] + w // 2, top_left[1] + h // 2)

                    debug_img = cv2.rectangle(img.copy(), top_left,
                                              (top_left[0] + w, top_left[1] + h),
                                              (0, 255, 0), 3)
                    cv2.imwrite(f"DEBUG_CYCLE_{cycle_num}_ATTEMPT_{attempt_num}_MATCH_{template_name}.png", debug_img)
                    return center
                return None
            except Exception as e:
                log(f"Ошибка поиска: {str(e)}", "ERROR")
                return None

        def check_restart_trigger():
            try:
                screenshot = pyautogui.screenshot()
                img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                res = cv2.matchTemplate(gray, templates["RestartTrigger"], cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(res)
                return max_val >= threshold
            except:
                return False

        cycle_number = 1
        while True:
            log(f"════════ ЦИКЛ {cycle_number} ════════", "HEADER")
            restart_requested = False

            # Этап 0: Ожидание перед началом нового цикла
            log("Ожидание перед началом нового цикла", "DEBUG")
            time.sleep(3)
            pyautogui.press('m')

            # Этап 1: Поиск KPK
            attempt = 1
            while True:
                if check_restart_trigger():
                    log("Обнаружен RestartTrigger → Перезапуск цикла", "WARNING")
                    time.sleep(3)
                    pyautogui.press('m')
                    restart_requested = True
                    break
                log(f"Поиск KPK | Попытка {attempt}")
                pos = enhanced_find_template("KPK", cycle_number, attempt)
                if pos:
                    pyautogui.moveTo(pos)
                    pyautogui.click()
                    time.sleep(2.5)
                    break
                attempt += 1
                time.sleep(3)
            if restart_requested:
                continue

            # Этап 2: Принятие заказа
            attempt = 1
            while True:
                if check_restart_trigger():
                    log("Обнаружен RestartTrigger → Перезапуск цикла", "WARNING")
                    time.sleep(3)
                    pyautogui.press('m')
                    restart_requested = True
                    break
                log(f"Поиск кнопки принятия | Попытка {attempt}")
                pos = enhanced_find_template("TaxiAccept", cycle_number, attempt)
                if pos:
                    pyautogui.moveTo(pos)
                    pyautogui.click()
                    time.sleep(3)
                    break
                attempt += 1
                time.sleep(3)
            if restart_requested:
                continue

            # Этап 3: Завершение заказа (ZakazGotov)
            attempt = 1
            while True:
                if check_restart_trigger():
                    log("Обнаружен RestartTrigger → Перезапуск цикла", "WARNING")
                    time.sleep(3)
                    pyautogui.press('m')
                    restart_requested = True
                    break
                log(f"Поиск завершения | Попытка {attempt}")
                pos = enhanced_find_template("ZakazGotov", cycle_number, attempt)
                if pos:
                    log("Обнаружен ZakazGotov → перезапуск цикла через 3 сек.", "INFO")
                    time.sleep(3)
                    pyautogui.press('m')
                    cycle_number += 1
                    break
                attempt += 1
                time.sleep(3)
            if restart_requested:
                continue

    except Exception as e:
        log(f"КРИТИЧЕСКАЯ ОШИБКА: {str(e)}", "CRITICAL")
        raise


if __name__ == "__main__":
    if "--service=taxi" in sys.argv:
        try:
            run_taxi()
        except KeyboardInterrupt:
            print("\n[TAXI] Работа прервана пользователем")
        except Exception as e:
            print(f"[TAXI] Фатальная ошибка: {str(e)}")
            sys.exit(1)
    else:
        print("[TAXI] Сервис не активирован")
