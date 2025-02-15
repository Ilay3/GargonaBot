import json
import time
import os
import pyautogui
import threading

# Функция для загрузки настроек из settings.json
def load_settings(path):
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Функция для поиска изображения на экране и клика по его центру
def find_and_click(image_name, offset_x=0, offset_y=0, confidence=0.8):
    image_path = os.path.join('../../../resources/images/ImgFullReconect', image_name)

    try:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        if location:
            x, y = location
            print(f"Изображение {image_name} найдено на координатах {x}, {y}")

            # Устанавливаем курсор в найденные координаты и выполняем клик
            pyautogui.moveTo(x + offset_x, y + offset_y)
            time.sleep(0.5)  # Задержка перед кликом
            pyautogui.click()
            print(f"Клик по изображению {image_name}.")
            return True
    except pyautogui.ImageNotFoundException:
        pass

    return False

# Функция для поиска image2 и image21 одновременно
def search_images_concurrently():
    image2_found = False
    image21_found = False

    while not (image2_found or image21_found):  # Ждём нахождения хотя бы одной из картинок
        if not image2_found:
            image2_found = find_and_click('image2.png')

        if not image21_found:
            image21_found = find_and_click('image21.png')

        if image2_found or image21_found:
            print("Найдено одно из изображений: image2 или image21. Переход к следующему этапу.")
            return  # Выход из функции

        print("image2 и image21 не найдены, пробуем снова...")
        time.sleep(1)  # Задержка между попытками

# Основная логика программы
def main(settings_path):
    settings = load_settings(settings_path)

    # Поиск и клик по image1
    while not find_and_click('image1.png'):
        print("image1 не найдено, повторяю клик...")
        time.sleep(1)

    time.sleep(1)

    # Поиск image2 и image21 одновременно, продолжаем выполнение после нахождения хотя бы одного
    search_images_concurrently()

    time.sleep(1)

    # Продолжаем выполнение после нахождения image2 или image21
    print("Продолжаем выполнение программы...")

    # Ожидание, пока image6 не будет найдено
    while not find_and_click('image6.png'):
        print("image6 не найдено, пробуем снова...")
        time.sleep(1)

    print("Дополнительная картинка найдена, продолжаем выполнение.")

    time.sleep(1)
    # Поиск и клик по image3 с отступом по X
    if find_and_click('image3.png', offset_x=30):
        time.sleep(1)

        # Ввод пароля
        pyautogui.write(settings['password'])
        time.sleep(1)

        # Поиск и клик по image4
        if not find_and_click('image5.png'):
            print("Ошибка: Картинка 4 не найдена")
        else:
            print("Картинка 4 найдена и нажата.")
            time.sleep(1)

        # Определение координат для выбора персонажа
        character_positions = {
            "First": (1565, 368),
            "Second": (1565, 526),
            "Third": (1565, 695)
        }

        character = settings['character']
        if character in character_positions:
            x, y = character_positions[character]
            pyautogui.click(x, y)
            time.sleep(1)

            # Поиск и клик по image5
            if not find_and_click('image4.png'):
                print("Ошибка: Картинка 5 не найдена")
            else:
                print("Картинка 5 найдена и нажата.")
                time.sleep(1)

            # Чтение точки спауна из settings.json
            spawn = settings.get('spawn', 'Dom')

            # Словарь картинок для каждой точки спауна
            spawn_images = {
                "Dom": ['dom.png'],
                "Kvartira": ['kvartira.png'],
                "Spawn": ['spawn.png'],
                "Lasttochka": ['lasttochka.png']
            }

            # Получаем список картинок для выбранной точки спауна
            images_to_search = spawn_images.get(spawn, spawn_images['Dom'])

            # Бесконечный поиск и клик по картинкам для выбранной точки спауна
            for image in images_to_search:
                while not find_and_click(image):
                    print(f"{image} не найдено, пробуем снова...")
                    time.sleep(1)
                print(f"{image} найдено и нажато.")

            # Бесконечный поиск и клик по image7.png
            while not find_and_click('image7.png'):
                print("image7 не найдено, пробуем снова...")
                time.sleep(1)

            print("Дополнительная картинка image7 найдена, продолжаем выполнение.")


if __name__ == "__main__":
    settings_path = '../../../settings.json'
    main(settings_path)
