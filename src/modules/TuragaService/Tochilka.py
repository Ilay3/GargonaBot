import pyautogui
import cv2
import numpy as np
import time
import os

# Путь к изображению для поиска
image_path = os.path.join('../../../resources/images/ImgTochilka/palka.png')

# Установим точность поиска изображения (обычно от 0.5 до 1)
confidence = 0.8

# Область для поиска (по аналогии с координатами в AHK)
search_region = (657, 670, 1260, 977)


# Начало работы скрипта
def find_and_move():
    while True:
        # Сделаем скриншот области экрана, в которой будем искать изображение
        screenshot = pyautogui.screenshot(region=search_region)
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

        # Загрузим изображение и конвертируем его в формат, который понимает OpenCV
        template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # Прочитаем изображение в оттенках серого
        if template is None:
            print(f"Ошибка при загрузке изображения: {image_path}")
            return

        # Преобразуем оба изображения в нужный формат
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        # Ищем изображение в скриншоте
        result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= confidence)

        # Если изображение найдено
        if len(loc[0]) > 0:
            # Берем первую найденную позицию (можно изменить логику)
            found_x, found_y = loc[1][0] + search_region[0], loc[0][0] + search_region[1]

            # Смещаем курсор на те же X координаты, но на 20 пикселей ниже по Y
            move_x = found_x + 20
            move_y = found_y + 50

            # Перемещаем мышь на новые координаты с ускорением
            pyautogui.moveTo(move_x, move_y, duration=0.01)  # Уменьшено время на перемещение

        # Немного ждем перед следующим циклом
        time.sleep(0.001)


# Запуск
if __name__ == '__main__':
    find_and_move()
