import os
import random
import time
import logging
import pydirectinput

# Формируем путь к папке logs относительно текущего файла antiafk.py:
log_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "logs")
# Создаём папку, если её нет:
os.makedirs(log_dir, exist_ok=True)

# Полный путь к лог-файлу
log_file = os.path.join(log_dir, "antiafk.txt")


# Настройка логирования
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
)


# Список возможных клавиш
keys = ['w', 'a', 's', 'd']


# Логирование старта программы
logging.info("Запуск программы для случайного эмуляции нажатия клавиш.")

while True:
    try:
        logging.debug("Начало цикла ожидания.")

        key = random.choice(keys)
        logging.debug(f"Выбрана клавиша: {key}")

        # Эмулируем нажатие клавиши
        pydirectinput.keyDown(key)
        pydirectinput.keyUp(key)
        logging.info(f"Эмулирована клавиша: {key}")

        print(f"Эмулирована клавиша: {key}")

        time.sleep(240)  # Пауза между нажатиями

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        print(f"Произошла ошибка: {e}")
        break

logging.info("Завершение программы.")
