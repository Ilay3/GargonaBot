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
    """Проверка только боковых пикселей с улучшенным определением зоны"""
    try:
        # Обновленные координаты на основе логов
        left_x, right_x = 956, 963
        y = 495

        # Цвета из ваших логов
        target_green = (126, 211, 33)
        tolerance = 15  # Более строгий допуск

        def is_green(pixel):
            return all(abs(pixel[i] - target_green[i]) <= tolerance for i in range(3))

        left_green = is_green(pyautogui.pixel(left_x, y))
        right_green = is_green(pyautogui.pixel(right_x, y))

        # Логирование для диагностики
        print(f"Левый ({left_x},{y}): {left_green} | Правый ({right_x},{y}): {right_green}")

        # Активируем когда оба крайних пикселя зеленые
        if left_green and right_green:
            pyautogui.press('e')
            print("!!! УСПЕШНОЕ СРАБАТЫВАНИЕ !!!")
            time.sleep(0.07)  # Оптимальная задержка
            return True

        return False

    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return False

def run_port():




    print("Сервис Порт: Инициализация...")
    search_region = (583, 986, 1390, 1060)  # Область поиска кнопок

    try:
        while True:
            # Поиск кнопки "Работа"


                while True:
                    # Проверка пикселей и нажатие клавиш
                    pixel_check()



                    time.sleep(0.01)



    except KeyboardInterrupt:
        print("Работа сервиса прервана пользователем")
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    if "--service" in sys.argv:
        print("Запуск сервиса схем в сервисном режиме")
        run_port()
        print("Сервис схем завершил работу")
    else:
        print("Для запуска используйте флаг --service")