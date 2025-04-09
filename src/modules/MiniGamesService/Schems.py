import cv2
import numpy as np
import pyautogui
import time
import sys
import os
from datetime import datetime

pyautogui.FAILSAFE = False

# Получаем абсолютный путь к директории скрипта
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def log(message):
    """Логирование сообщений с временной меткой"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")


def load_image(image_name):
    """Загрузка изображений из папки resources"""
    resources_path = os.path.join(SCRIPT_DIR, "..", "..", "resources", "images", "ImgSchems", image_name)
    image = cv2.imread(resources_path, 0)
    if image is None:
        log(f"ОШИБКА: Не удалось загрузить изображение {image_name} из {resources_path}")
    return image


def find_template(template, threshold=0.8, region=None):
    """Поиск шаблона на экране"""
    try:
        screenshot = pyautogui.screenshot(region=region) if region else pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
        return np.any(res >= threshold)
    except Exception as e:
        log(f"Ошибка при поиске шаблона: {str(e)}")
        return False


def pixel_check():
    """Проверка цвета пикселей и нажатие клавиши E"""
    try:
        x, y = 959, 495  # Центральные координаты
        right = pyautogui.pixel(963, 495)
        left = pyautogui.pixel(956, 495)
        mid = pyautogui.pixel(x, y)

        if right == (126, 211, 33) and left == (126, 211, 33):
            pyautogui.press('e')
        elif mid != (231, 33, 57):
            pyautogui.press('e')
    except Exception as e:
        log(f"Ошибка при проверке пикселей: {str(e)}")


def run_schemas():
    """Основная логика работы сервиса схем"""
    # Загрузка шаблонов
    template_rabota = load_image("Rabota.png")
    template_stop = load_image("StopButton.png")

    # Проверка загрузки изображений
    if template_rabota is None or template_stop is None:
        log("Критическая ошибка: отсутствуют необходимые изображения")
        sys.exit(1)

    log("Сервис схем: Инициализация...")
    search_region = (583, 986, 1390, 1060)  # Область поиска кнопок

    try:
        while True:
            # Поиск кнопки "Работа"
            if find_template(template_rabota, threshold=0.8):
                log("Активация режима работы со схемами")
                last_check = time.time()

                while True:
                    # Проверка пикселей и нажатие клавиш
                    pixel_check()

                    # Проверка кнопки "Стоп" каждые 100 мс
                    if time.time() - last_check >= 0.1:
                        if find_template(template_stop, 0.8, search_region):
                            log("Обнаружена кнопка остановки")
                            return
                        last_check = time.time()

                    time.sleep(0.01)  # Снижение нагрузки на CPU

            time.sleep(0.5)  # Пауза между проверками

    except KeyboardInterrupt:
        log("Работа сервиса прервана пользователем")
    except Exception as e:
        log(f"Критическая ошибка: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    if "--service" in sys.argv:
        log("Запуск сервиса схем в сервисном режиме")
        run_schemas()
        log("Сервис схем завершил работу")
    else:
        log("Для запуска используйте флаг --service")