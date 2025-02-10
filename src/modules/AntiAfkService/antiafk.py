import random
import time
import logging
import pydirectinput

# Настройка логирования
logging.basicConfig(
    filename='../../../logs/antiafk.txt',
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

        time.sleep(5)  # Пауза между нажатиями

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        print(f"Произошла ошибка: {e}")
        break

logging.info("Завершение программы.")
