import pyautogui
from PIL import Image, ImageDraw, ImageFont
import time
from collections import Counter


def find_and_mark_image(image_path):
    while True:
        print(f"Ищу изображение: {image_path}")
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=0.8)

            if location:
                print(f"Найдено изображение! Координаты: {location}")

                # Получаем координаты левого верхнего угла и правого нижнего угла
                left, top, width, height = location.left, location.top, location.width, location.height
                right, bottom = left + width, top + height

                # 4 точки границы зоны
                points = [
                    (left, top),  # Левый верхний угол
                    (right, top),  # Правый верхний угол
                    (left, bottom),  # Левый нижний угол
                    (right, bottom)  # Правый нижний угол
                ]

                # Делаем скриншот всего экрана
                screenshot = pyautogui.screenshot()

                # Преобразуем скриншот в объект Image (для редактирования)
                screenshot = Image.frombytes('RGB', screenshot.size, screenshot.tobytes())

                # Определяем преобладающий цвет в области
                region = screenshot.crop((left, top, right, bottom))
                dominant_color = get_dominant_color(region)

                # Выводим преобладающий цвет в консоль
                print(f"Преобладающий цвет в области: #{dominant_color}")

                # Рисуем линии между четырьмя точками
                draw = ImageDraw.Draw(screenshot)

                # Рисуем линии между точками
                draw.line([points[0], points[1]], fill="red", width=5)  # Верхняя линия
                draw.line([points[1], points[3]], fill="red", width=5)  # Правая линия
                draw.line([points[3], points[2]], fill="red", width=5)  # Нижняя линия
                draw.line([points[2], points[0]], fill="red", width=5)  # Левая линия

                # Добавляем текст с координатами для каждой точки
                font = ImageFont.load_default()  # Используем стандартный шрифт
                for i, point in enumerate(points):
                    text = f"({point[0]}, {point[1]})"
                    draw.text((point[0] + 5, point[1] - 15), text, fill="red", font=font)

                # Добавляем текст с преобладающим цветом
                draw.text((left, top - 40), f"Цвет: #{dominant_color}", fill="red", font=font)

                # Сохраняем изображение с выделенной областью и текстом
                screenshot.save("highlighted_screenshot.png")
                screenshot.show()

                break  # Завершаем цикл, если изображение найдено
            else:
                print("Изображение не найдено, продолжаю поиск...")
                time.sleep(2)  # Задержка 2 секунды перед повторной попыткой

        except pyautogui.ImageNotFoundException:
            print("Ошибка: изображение не найдено на экране.")
            break  # Выход из цикла в случае ошибки, если изображение не найдено


def get_dominant_color(region):
    # Преобразуем регион в список пикселей
    pixels = list(region.getdata())

    # Используем Counter для подсчета частоты каждого цвета
    color_counts = Counter(pixels)

    # Находим наиболее часто встречающийся цвет
    dominant_color = color_counts.most_common(1)[0][0]

    # Преобразуем цвет в формат HEX
    return ''.join(f'{c:02x}' for c in dominant_color)


# Пример использования
image_path = r'C:\Users\Ilya\PycharmProjects\GargonaBot\resources\images\ImgFerma\template_d.png'
find_and_mark_image(image_path)
