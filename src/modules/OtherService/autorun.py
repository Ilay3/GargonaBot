import time
import logging
import pydirectinput
import keyboard  # Для отслеживания нажатия клавиш
import threading

# Настройка логирования
logging.basicConfig(
    filename='../../../logs/autoran.txt',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

# Логирование старта программы
logging.info("Запуск программы для эмуляции зажатия клавиш.")

# Флаг для аварийной остановки
emergency_stop = False
is_p_pressed = False

# Функция для аварийной остановки программы
def emergency_stop_listener():
    global emergency_stop
    logging.info("Запуск прослушивания аварийной кнопки.")
    while True:
        if keyboard.is_pressed('esc'):  # Нажатие 'esc' для аварийной остановки
            emergency_stop = True
            logging.info("Аварийная остановка программы.")
            break
        time.sleep(0.1)

# Поток для прослушивания аварийной кнопки
stop_thread = threading.Thread(target=emergency_stop_listener, daemon=True)
stop_thread.start()

# Эмуляция зажатия клавиш
while True:
    try:
        logging.debug("Начало цикла ожидания.")

        # Если нажата клавиша 'p' и клавиши ещё не зажаты, начинаем эмуляцию
        if keyboard.is_pressed('p') and not emergency_stop and not is_p_pressed:
            is_p_pressed = True
            logging.debug("Нажата клавиша 'p'. Эмуляция зажатия 'w' + 'shift'.")
            pydirectinput.keyDown('w')
            pydirectinput.keyDown('shift')
            print("Нажата клавиша: 'w' и 'shift'")  # Вывод в консоль
            logging.info("Зажаты клавиши 'w' + 'shift'.")

        # Если клавиша 'p' отпущена, но клавиши уже зажаты, продолжаем удержание
        if is_p_pressed and not emergency_stop:
            print("Продолжаем удержание клавиш: 'w' и 'shift'")  # Вывод в консоль
            time.sleep(0.1)  # Задержка для стабильности

        # Остановить эмуляцию, если нажата клавиша для аварийной остановки или программа завершена
        if emergency_stop:
            logging.info("Завершаем программу.")
            pydirectinput.keyUp('shift')
            pydirectinput.keyUp('w')
            print("Отпущены клавиши: 'w' и 'shift'")  # Вывод в консоль
            break

        # Пауза, чтобы не перегружать процессор
        time.sleep(0.1)

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        print(f"Произошла ошибка: {e}")
        break

# Завершение программы
logging.info("Завершение программы.")
