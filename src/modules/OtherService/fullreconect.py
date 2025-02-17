import json
import time
import os
import pyautogui
from datetime import datetime
import pytz

pyautogui.FAILSAFE = False  # Отключение аварийного завершения

SETTINGS_PATH = '../../../settings.json'  # Путь к файлу настроек

# Добавляем импорт модуля process_checker для проверки активности игры.
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "ProcessChecker"))
import process_checker

def check_settings(path):
    """Проверяет наличие settings.json и запрашивает недостающие данные."""
    default_settings = {
        "password": "",
        "character": "",
        "spawn": "",
        "rage_mp_path": ""  # Путь до ярлыка Rage MP
    }

    if not os.path.exists(path):
        print("Файл settings.json не найден. Создаю новый.")
        settings = default_settings
    else:
        with open(path, 'r', encoding='utf-8') as file:
            try:
                settings = json.load(file)
            except json.JSONDecodeError:
                print("Ошибка чтения JSON. Пересоздаю файл.")
                settings = default_settings

    # Проверяем наличие всех ключей и их заполненность
    for key in default_settings:
        if key not in settings or not settings[key]:
            settings[key] = input(f"Введите значение для {key}: ")

    # Сохраняем обновлённые настройки
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(settings, file, indent=4, ensure_ascii=False)

    return settings

def find_and_click(image_name, offset_x=0, offset_y=0, confidence=0.8, double_click=False):
    image_path = os.path.join('../../../resources/images/ImgFullReconect', image_name)
    while True:
        try:
            location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
            if location:
                x, y = location
                pyautogui.click(x + offset_x, y + offset_y)
                print(f"Изображение {image_name} найдено и кликнуто.")
                return True
        except pyautogui.ImageNotFoundException:
            print(f"Не удалось найти {image_name}, пробую снова...")
        time.sleep(1)

def main(settings_path):
    settings = check_settings(settings_path)

    # --- Новый блок: запуск ярлыка Rage MP, если игра не запущена ---
    if not process_checker.is_game_active():
        shortcut = settings.get("rage_mp_path", "").strip()
        if shortcut:
            if not os.path.exists(shortcut) or not shortcut.lower().endswith(".lnk"):
                print("Неверный путь или расширение ярлыка. Укажите корректный путь до .lnk файла.")
            else:
                try:
                    os.startfile(shortcut, "runas")
                    print("Ярлык запущен.")
                    # Ждем несколько секунд, чтобы лаунчер успел открыться
                    time.sleep(10)
                except Exception as e:
                    print("Ошибка при запуске ярлыка:", e)
        else:
            print("Путь до ярлыка не задан в настройках.")
    else:
        print("Игра уже запущена.")

    # Далее начинаем автоматизацию через распознавание изображений в окне лаунчера

    # Ждем, пока не найдется image1.png
    while not find_and_click('image1.png'):
        time.sleep(1)

    time.sleep(1)
    # Запускаем конкурентный поиск изображений (image2.png или image21.png)
    while True:
        if find_and_click('image21.png'):
            break
        time.sleep(1)

    time.sleep(1)
    # Ждем, пока не найдется image6.png
    while not find_and_click('image6.png'):
        time.sleep(1)

    time.sleep(1)
    if find_and_click('image3.png', offset_x=30):
        time.sleep(1)
        pyautogui.write(settings['password'])
        time.sleep(1)
        if not find_and_click('image5.png'):
            print("Ошибка: Дополнительная кнопка не найдена")
            time.sleep(5)
        else:
            time.sleep(1)
        character_positions = {
            "First": (1565, 368),
            "Second": (1565, 526),
            "Third": (1565, 695)
        }
        if settings['character'] in character_positions:
            x, y = character_positions[settings['character']]
            pyautogui.click(x, y)
            time.sleep(1)
            if not find_and_click('image4.png'):
                print("Ошибка: Картинка 4 не найдена")
            else:
                time.sleep(1)
        else:
            print("Ошибка: Некорректное значение character в настройках")
        spawn_images = {
            "Dom": ['dom.png'],
            "Kvartira": ['kvartira.png'],
            "Spawn": ['spawn.png'],
            "Lasttochka": ['lasttochka.png']
        }
        for image in spawn_images.get(settings['spawn'], spawn_images['Dom']):
            if not find_and_click(image):
                print(f"Ошибка: {image} не найдена")
                break
            time.sleep(1)
        if find_and_click('image7.png'):
            print("image7.png найдена и нажата.")
        else:
            print("Ошибка: image7.png не найдена")
    else:
        print("Ошибка: Картинка 3 не найдена")

if __name__ == "__main__":
    main(SETTINGS_PATH)
