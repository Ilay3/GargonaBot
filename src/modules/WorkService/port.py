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


def run_port():




    log("Сервис Порт: Инициализация...")
    search_region = (583, 986, 1390, 1060)  # Область поиска кнопок

    try:
        while True:
            # Поиск кнопки "Работа"


                while True:
                    # Проверка пикселей и нажатие клавиш
                    pixel_check()



                    time.sleep(0.01)



    except KeyboardInterrupt:
        log("Работа сервиса прервана пользователем")
    except Exception as e:
        log(f"Критическая ошибка: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    if "--service" in sys.argv:
        log("Запуск сервиса схем в сервисном режиме")
        run_port()
        log("Сервис схем завершил работу")
    else:
        log("Для запуска используйте флаг --service")