import cv2
import numpy as np
import pyautogui
import time
from datetime import datetime

# Загружаем эталонные изображения в градациях серого
templates = [
    cv2.imread('../../../resources/images/ImgKachalka/Circle2.png', 0),
]

def log(message):
    """Выводит сообщение с текущим временем в консоль."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def find_template_on_screen(template, threshold=0.84):
    """Ищет шаблон на экране, возвращает True, если найдено."""
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    if len(loc[0]) > 0:
        log(f"Совпадение найдено! Координаты: {list(zip(loc[1], loc[0]))}")
        return True
    else:
        return False

def display_menu():
    """Отображает меню выбора."""
    print("Выберите тип спортплощадки:")
    print("1) Дешевая спортплощадка (Пирс)")
    print("2) Средняя спортплощадка (Автошкола)")
    print("3) Дорогая спортплощадка (Вощле банка)")

    choice = input("Введите номер выбора (1, 2, 3): ")

    if choice == '1':
        log("Вы выбрали дешевую спортплощадку (Пирс).")
        return 1  # Можно добавить код для выбора соответствующего шаблона
    elif choice == '2':
        log("Вы выбрали среднюю спортплощадку (Автошкола).")
        return 2  # Можно добавить код для выбора соответствующего шаблона
    elif choice == '3':
        log("Вы выбрали дорогую спортплощадку (Вощле банка).")
        return 3  # Можно добавить код для выбора соответствующего шаблона
    else:
        log("Неверный выбор, попробуйте снова.")
        return display_menu()

# Выводим меню и получаем выбор пользователя
user_choice = display_menu()

# Бесконечный цикл поиска
while True:
    log("Запуск нового цикла поиска шаблонов...")

    # Запись времени начала цикла
    start_time = time.time()

    # Проходим по каждому шаблону и проверяем его на экране
    for idx, template in enumerate(templates):
        log(f"Ищем шаблон {idx+1}...")

        if find_template_on_screen(template):
            log(f"Шаблон {idx+1} найден! Ожидание 1 миллисекунду перед нажатием пробела...")
            time.sleep(0.001)  # Ожидание 1 миллисекунду
            pyautogui.press("space")
            log("Нажата клавиша пробела")

    # Запись времени завершения цикла
    end_time = time.time()
    cycle_duration = end_time - start_time
    log(f"Цикл поиска завершён. Время выполнения: {cycle_duration:.4f} секунд.")

    # Пауза перед следующим циклом
    time.sleep(0.001)  # Пауза в 1 миллисекунду перед следующей проверкой
