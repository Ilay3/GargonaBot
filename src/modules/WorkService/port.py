import cv2
import numpy as np
import pyautogui
import time
import sys
from datetime import datetime


def run_port(
    button_image_path="../../../resources/images/ImgPort/ButtonE.png",
    second_image_path="../../../resources/images/ImgPort/SecondImage.png",
    threshold=0.8,
):
    """
    Запускает процесс поиска шаблонов на экране:
    1. Ищет первую картинку (ButtonE) и нажимает 'E' через 0.3 секунды после её обнаружения.
    2. После нахождения первой картинки ищет вторую картинку.
    3. Если вторая картинка найдена, цикл поиска ButtonE начинается заново.

    :param button_image_path: Путь к изображению кнопки ButtonE.
    :param second_image_path: Путь ко второй картинке.
    :param threshold: Порог совпадения шаблона.
    """
    pyautogui.FAILSAFE = False

    def log(message):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

    def find_template_on_screen(template):
        """Ищет шаблон на экране и возвращает True, если найдено совпадение."""
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)

        if len(loc[0]) > 0:
            log(f"Совпадение найдено! Координаты: {list(zip(loc[1], loc[0]))}")
            return True
        return False

    # Загрузка шаблонов изображений
    button_template = cv2.imread(button_image_path, 0)
    second_template = cv2.imread(second_image_path, 0)

    if button_template is None:
        log(f"Ошибка: не удалось загрузить изображение кнопки {button_image_path}")
        return
    if second_template is None:
        log(f"Ошибка: не удалось загрузить второе изображение {second_image_path}")
        return

    log("Сервис запущен...")
    while True:
        # Поиск первой картинки (ButtonE)
        if find_template_on_screen(button_template):
            log("ButtonE найдена! Ожидание 0.3 секунды перед нажатием E...")
            time.sleep(0.7)  # Задержка 0.3 секунды
            pyautogui.press('e')  # Нажатие клавиши E
            log("Клавиша E нажата.")

            # Поиск второй картинки после обработки ButtonE
            log("Поиск второй картинки...")
            second_image_found = False
            while not second_image_found:
                if find_template_on_screen(second_template):
                    log("Вторая картинка найдена! Цикл поиска ButtonE начнётся заново.")
                    second_image_found = True
                time.sleep(0.1)  # Интервал проверки для второй картинки

            # После нахождения второй картинки цикл начинается заново
            continue

        # Интервал проверки, если ButtonE не найдена
        time.sleep(0.1)


if __name__ == "__main__":
    if "--service" in sys.argv:
        run_port()
    else:
        print("Флаг --service не передан, выход из программы.")