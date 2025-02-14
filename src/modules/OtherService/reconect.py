import json
import time
import pyautogui
import os
from PIL import Image


# Функция для загрузки настроек из settings.json
def load_settings(path):
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)


# Функция для поиска изображения на экране и клика по его центру
def find_and_click(image_name, offset_x=0, offset_y=0, confidence=0.8):
    image_path = os.path.join('../../../resources/images/ImgReconect',
                              image_name)  # Укажите путь к директории с изображениями

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

        time.sleep(1)  # Пауза между попытками


# Основная логика программы
def main(settings_path):
    settings = load_settings(settings_path)

    # Нажатие F1
    pyautogui.press('f1')
    time.sleep(1)

    # Поиск и нажатие на картинку 1
    if find_and_click('image1.png'):
        time.sleep(1)

        # Поиск и нажатие на картинку 2
        if find_and_click('image2.png'):
            time.sleep(1)

            # Поиск и нажатие на дополнительную картинку (например, image5.png)
            if not find_and_click('image6.png'):
                print("Ошибка: Дополнительная картинка не найдена")
                return  # Останавливаем выполнение, если дополнительная картинка не найдена

            print("Дополнительная картинка найдена и нажата.")
            time.sleep(1)

            # Поиск и нажатие на картинку 3 с отступом по X
            if find_and_click('image3.png', offset_x=30):
                time.sleep(1)

                # Ввод пароля
                pyautogui.write(settings['password'])
                time.sleep(1)

                # Поиск и нажатие на дополнительную кнопку после ввода пароля
                if not find_and_click('image5.png'):
                    print("Ошибка: Дополнительная кнопка не найдена")
                    time.sleep(5)
                else:
                    print("Дополнительная кнопка найдена и нажата.")
                    time.sleep(10)

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

                    # Поиск и нажатие на картинку 4
                    if not find_and_click('image4.png'):
                        print("Ошибка: Картинка 4 не найдена")
                else:
                    print("Ошибка: Некорректное значение character в settings.json")

                # Чтение точки спауна из settings.json
                spawn = settings.get('spawn', 'Dom')  # Если в JSON нет ключа 'spawn', по умолчанию будет 'Dom'

                # Словарь картинок для каждой точки спауна
                spawn_images = {
                    "Dom": ['dom.png'],
                    "Kvartira": ['kvartira.png'],
                    "Spawn": ['spawn.png'],
                    "Lasttochka": ['lasttochka.png']
                }

                # Получаем список картинок для выбранной точки спауна
                images_to_search = spawn_images.get(spawn, spawn_images['Dom'])  # По умолчанию используем 'Dom'

                # Последовательное распознавание и клик по картинкам
                for image in images_to_search:
                    if not find_and_click(image):
                        print(f"Ошибка: {image} не найдена")
                        break  # Прерываем, если картинка не найдена
                    print(f"{image} найдена и нажата.")
                    time.sleep(1)

                # Дополнительное распознавание и клик по картинке после выбора точки спауна
                additional_image = 'image7.png'  # Укажите название картинки для проверки
                if find_and_click(additional_image):
                    print(f"{additional_image} найдена и нажата.")
                else:
                    print(f"Ошибка: {additional_image} не найдена")

            else:
                print("Ошибка: Картинка 3 не найдена")
        else:
            print("Ошибка: Картинка 2 не найдена")
    else:
        print("Ошибка: Картинка 1 не найдена")


if __name__ == "__main__":
    settings_path = '../../../settings.json'  # Укажите путь к файлу
    main(settings_path)
