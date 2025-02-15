import json
import time
import pyautogui
import os
from datetime import datetime
import pytz

SETTINGS_PATH = '../../../settings.json'  # Путь к файлу настроек


def load_settings(path=SETTINGS_PATH):
    if not os.path.exists(path):
        print("Файл settings.json не найден. Создаю новый.")
        return {}
    with open(path, 'r', encoding='utf-8') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            print("Ошибка: Некорректный формат settings.json. Создаю новый.")
            return {}


def save_settings(path, settings):
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(settings, file, indent=4, ensure_ascii=False)


def find_and_click(image_name, offset_x=0, offset_y=0, confidence=0.8):
    image_path = os.path.join('../../../resources/images/ImgReconect', image_name)
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


def wait_for_correct_time():
    # Получаем текущее время в московской зоне
    moscow_tz = pytz.timezone('Europe/Moscow')
    while True:
        current_time = datetime.now(moscow_tz).strftime('%H:%M')
        if current_time == '07:10':
            print("Время 7:10 утра! Начинаю выполнение скрипта.")
            break
        else:
            print(f"Текущее время: {current_time}. Ожидаю 7:10 утра...")
        time.sleep(60)  # Проверяем время каждую минуту


def run_script(settings, wait_until_710=False):
    if wait_until_710:
        wait_for_correct_time()  # Ждем, пока не наступит 7:10 утра

    # Предполагается, что settings содержит ключи:
    # "password" – строка пароля,
    # "character" – "First", "Second" или "Third",
    # "spawn"     – "Dom", "Kvartira", "Spawn" или "Lasttochka".
    if 'password' not in settings or not settings['password']:
        raise ValueError("Пароль не задан в настройках.")
    if 'character' not in settings or settings['character'] not in ["First", "Second", "Third"]:
        raise ValueError("Некорректное значение персонажа.")
    if 'spawn' not in settings or settings['spawn'] not in ["Dom", "Kvartira", "Spawn", "Lasttochka"]:
        raise ValueError("Некорректное значение точки спауна.")

    pyautogui.press('f1')
    time.sleep(1)
    if not find_and_click('image1.png'):
        print("Ошибка: Картинка 1 не найдена")
        return
    time.sleep(1)
    if not find_and_click('image2.png'):
        print("Ошибка: Картинка 2 не найдена")
        return
    time.sleep(1)
    if not find_and_click('image6.png'):
        print("Ошибка: Дополнительная картинка не найдена")
        return
    time.sleep(1)
    if find_and_click('image3.png', offset_x=30):
        time.sleep(1)
        pyautogui.write(settings['password'])
        time.sleep(1)
        if not find_and_click('image5.png'):
            print("Ошибка: Дополнительная кнопка не найдена")
            time.sleep(5)
        else:
            time.sleep(10)
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
    settings = load_settings()

    # Спрашиваем пользователя, какой способ запуска он выбирает
    choice = input(
        "Какой способ запуска вам нужен? Введите '1' для немедленного запуска или '2' для ожидания 7:10 утра: ")

    if choice == '2':
        wait_until_710 = True
        print("Ожидаю 7:10 утра...")
    else:
        wait_until_710 = False
        print("Скрипт начнется немедленно.")

    # Запускаем скрипт с выбранным способом запуска
    run_script(settings, wait_until_710)
