import time
import pyautogui
import os
import keyboard  # Библиотека для отслеживания нажатий клавиш


# Функция для поиска изображения на экране
def find_image(image_name, confidence):
    image_path = os.path.join('../../../resources/images/ImgShveiaDemorgan', image_name)
    print(f"Ищу изображение: {image_name} с уверенностью: {confidence}, путь: {image_path}")  # Отладка
    try:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        if location:
            print(f"Изображение {image_name} найдено: {location}")
            return location
    except pyautogui.ImageNotFoundException:
        print(f"Изображение {image_name} не найдено.")
    return None


# Функция для выполнения клика по координатам
def click_at_location(location, repeat=False):
    if location:
        x, y = location
        pyautogui.click(x, y)
        print(f"Выполнен клик по координатам: ({x}, {y})")
        if repeat:
            time.sleep(0.5)
            pyautogui.click(x, y)
            print(f"Повторный клик по координатам: ({x}, {y})")


# Основная логика программы
def main():
    while True:  # Основной цикл, программа будет работать бесконечно, пока не завершится вручную
        print("Нажмите 'E' для начала работы программы...")

        # Ожидание нажатия клавиши 'E'
        while True:
            if keyboard.is_pressed('e'):
                print("Нажата клавиша 'E', начинаем выполнение программы.")
                break
            time.sleep(0.1)  # Пауза, чтобы не нагружать процессор

        # Теперь программа будет работать после нажатия 'E'
        image_confidences = {
            'image1.png': 0.95,  # Установим уверенность на 0.95 для всех изображений
            'image2.png': 0.95,
            'image3.png': 0.95,
            'image4.png': 0.95,
            'image5.png': 0.95,
            'image6.png': 0.95,
            'image7.png': 0.95,
            'image8.png': 0.95,
            'image9.png': 0.95,
            'image10.png': 0.95,
            'image11.png': 0.95,
            'image12.png': 0.95,
            'image13.png': 0.95,
            'image14.png': 0.95,
            'image15.png': 0.95,
            'image16.png': 0.95,
            'image17.png': 0.95,
            'image18.png': 0.95,
            'image19.png': 0.95,
            'image20.png': 0.95
        }

        locations = {}  # Словарь для хранения координат изображений

        # Этап 1: Поиск всех изображений и сохранение координат
        for image, confidence in image_confidences.items():
            location = find_image(image, confidence)

            # Если не нашли с уверенностью 0.95, пробуем с пониженной уверенностью 0.90
            if not location and confidence == 0.95:
                print(f"Не удалось найти {image} с уверенностью 0.95, пробую с 0.90...")
                location = find_image(image, 0.90)

            if location:
                locations[image] = location

        # Этап 2: Последовательное нажатие по найденным точкам
        for image, location in locations.items():
            click_at_location(location, repeat=image not in ['image1.png', 'image20.png'])

        print("Процесс завершен. Пауза на 10 секунд...")

        # Пауза на 10 секунд перед повтором
        time.sleep(10)


if __name__ == "__main__":
    main()
