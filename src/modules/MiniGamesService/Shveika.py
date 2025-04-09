import cv2
import numpy as np
import pyautogui
import time
import sys
import os
from datetime import datetime

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_path, relative_path)
    return full_path.replace('\\', os.sep) if os.sep == '/' else full_path.replace('/', os.sep)

# Глобальная функция логирования
def log(message):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

print("Shveika.py запущен как скрипт. Аргументы: " + str(sys.argv))

def run_shveika(
        button_w_path=get_resource_path("resources/images/ImgShveika/ButtonW.png"),
        button_a_path=get_resource_path("resources/images/ImgShveika/ButtonA.png"),
        button_s_path=get_resource_path("resources/images/ImgShveika/ButtonS.png"),
        button_d_path=get_resource_path("resources/images/ImgShveika/ButtonD.png"),
        start_work_path=get_resource_path("resources/images/ImgShveika/StartWork.png"),
        stop_work_path=get_resource_path("resources/images/ImgShveika/StopWork.png"),
        threshold=0.9,

):
    print("Функция run_shveika запущена.")
    pyautogui.FAILSAFE = False

    # Сопоставление изображений с кнопками (добавлено в правильное место)
    key_mapping = {
        "ButtonW": "w",
        "ButtonA": "a",
        "ButtonS": "s",
        "ButtonD": "d"
    }

    def find_template_on_screen(template, template_name):
        """Модифицированная функция с логированием результатов поиска"""
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)

        max_val = np.max(res)
        log(f"Поиск {template_name}: Максимальное совпадение = {max_val:.2f}, порог = {threshold}")

        if len(loc[0]) > 0:
            log(f"Совпадение найдено! {template_name} Координаты: {list(zip(loc[1], loc[0]))}")
            return True
        log(f"Совпадение для {template_name} не найдено")
        return False

    def check_file_exists(path):
        if not os.path.exists(path):
            log(f"ФАЙЛ НЕ НАЙДЕН: {path}")
            return False
        return True

    # Преобразование путей
    script_dir = os.path.dirname(os.path.abspath(__file__))
    paths = {
        "ButtonW": button_w_path,
        "ButtonA": button_a_path,
        "ButtonS": button_s_path,
        "ButtonD": button_d_path,
        "StartWork": start_work_path,
        "StopWork": stop_work_path,
    }
    # Загрузка шаблонов
    templates = {
        "ButtonW": cv2.imread(paths["ButtonW"], 0),
        "ButtonA": cv2.imread(paths["ButtonA"], 0),
        "ButtonS": cv2.imread(paths["ButtonS"], 0),
        "ButtonD": cv2.imread(paths["ButtonD"], 0),
        "StartWork": cv2.imread(paths["StartWork"], 0),
        "StopWork": cv2.imread(paths["StopWork"], 0),
    }
    # Проверка существования файлов
    for name, path in paths.items():
        full_path = os.path.abspath(os.path.join(script_dir, path))
        log(f"[LOAD CHECK] {name}: {full_path}")
        if not os.path.exists(full_path):
            log(f"[ERROR] Файл не найден: {name} -> {full_path}")
            return
        image = cv2.imread(full_path, 0)
        if image is None:
            log(f"[ERROR] Не удалось загрузить изображение {name}: {full_path}")
            return
        templates[name] = image
        log(f"Изображение {name} успешно загружено. Размер: {image.shape}")



    # Проверка загрузки изображенийe
    for key, template in templates.items():
        if template is None:
            log(f"Ошибка загрузки изображения: {key}")
            return
        log(f"Изображение {key} успешно загружено. Размер: {template.shape}")

    # Основной цикл
    log("Сервис запущен...")
    not_found_time = time.time()
    last_state = None

    while True:
        current_state = []
        found_letter = False  # Добавлена инициализация переменной

        # Проверка WASD
        for key in ["ButtonW", "ButtonA", "ButtonS", "ButtonD"]:
            found = find_template_on_screen(templates[key], key)
            current_state.append(f"{key}: {'найдено' if found else 'нет'}")
            if found:
                log(f"Обнаружена кнопка {key} -> нажатие {key_mapping[key]}")
                pyautogui.press(key_mapping[key])
                not_found_time = time.time()
                found_letter = True

        # Проверка StartWork
        if time.time() - not_found_time >= 3:
            found_start = find_template_on_screen(templates["StartWork"], "StartWork")
            current_state.append(f"StartWork: {'найдено' if found_start else 'нет'}")
            if found_start:
                log("Найдена StartWork -> нажатие E")
                pyautogui.press('e')
                not_found_time = time.time()
        else:
            current_state.append(f"StartWork: проверка заблокирована (таймер)")

        # Проверка StopWork
        found_stop = find_template_on_screen(templates["StopWork"], "StopWork")
        current_state.append(f"StopWork: {'найдено' if found_stop else 'нет'}")
        if found_stop:
            log("Обнаружен StopWork -> завершение работы")
            break

        # Логирование изменений состояния
        new_state = ", ".join(current_state)
        if new_state != last_state:
            log(f"Текущее состояние: {new_state}")
            last_state = new_state

        time.sleep(0.1)


if __name__ == "__main__":
    log("Shveika.py: Проверка аргументов запуска...")
    if "--service=shveika" in sys.argv:
        print("--service=shveika найден в аргументах, вызываем run_shveika()")
        run_shveika()
    else:
        print("Флаг --service=shveika не передан, выход из программы.")
