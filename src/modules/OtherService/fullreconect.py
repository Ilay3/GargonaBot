import json
import time
import os
import pyautogui

pyautogui.FAILSAFE = False  # Отключение аварийного завершения


def check_settings(path):
    """Проверяет наличие settings.json и запрашивает недостающие данные."""
    default_settings = {
        "password": "",
        "character": "",
        "spawn": ""
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
    try:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        if location:
            x, y = location
            pyautogui.moveTo(x + offset_x, y + offset_y)
            time.sleep(0.5)
            pyautogui.click()
            if double_click:
                time.sleep(0.2)
                pyautogui.click()
            return True
    except pyautogui.ImageNotFoundException:
        pass
    return False


def search_images_concurrently():
    while True:
        if find_and_click('image2.png') or find_and_click('image21.png'):
            return
        time.sleep(1)


def main(settings_path):
    settings = check_settings(settings_path)



    while not find_and_click('image1.png'):
        time.sleep(1)

    time.sleep(1)
    search_images_concurrently()
    time.sleep(1)

    while not find_and_click('image6.png'):
        time.sleep(1)

    time.sleep(1)
    if find_and_click('image3.png', offset_x=30):
        time.sleep(1)
        pyautogui.write(settings['password'])
        time.sleep(1)

        if not find_and_click('image5.png'):
            print("Ошибка: Картинка 4 не найдена")
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
                print("Ошибка: Картинка 5 не найдена")
            else:
                time.sleep(1)

        spawn_images = {
            "Dom": ['dom.png'],
            "Kvartira": ['kvartira.png'],
            "Spawn": ['spawn.png'],
            "Lasttochka": ['lasttochka.png']
        }

        for image in spawn_images.get(settings['spawn'], ['dom.png']):
            while not find_and_click(image):
                time.sleep(1)

        while not find_and_click('image7.png'):
            time.sleep(1)


if __name__ == "__main__":
    settings_path = '../../../settings.json'
    main(settings_path)
