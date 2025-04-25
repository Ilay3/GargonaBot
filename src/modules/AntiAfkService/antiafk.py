import os
import random
import time
import logging
import sys
import platform
from datetime import datetime
import pydirectinput


def run_antiafk(
        keys=['w', 'a', 's', 'd'],
        interval=180,
        log_file=None
):
    """
    Сервис для эмуляции случайных нажатий клавиш с логированием и обработкой ошибок.
    """

    # Внутренняя функция логирования
    def log(message, level="info"):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        if level == "info":
            logging.info(log_message)
        elif level == "error":
            logging.error(log_message)
        elif level == "debug":
            logging.debug(log_message)

    # Проверка ОС
    if platform.system() != "Windows":
        log("Скрипт поддерживает только Windows.", "error")
        return

    # Настройка путей
    if log_file is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.join(base_dir, "..", "..", "..", "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "antiafk.txt")

    # Инициализация логирования
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )

    log("Запуск Anti-AFK сервиса...")
    log(f"Используемые клавиши: {', '.join(keys)}")
    log(f"Интервал нажатий: {interval} сек")

    try:
        while True:
            try:
                # Выбор и эмуляция клавиши
                key = random.choice(keys)
                log(f"Эмуляция нажатия клавиши: {key}", "debug")

                pydirectinput.keyDown(key)
                pydirectinput.keyUp(key)
                log(f"Успешно эмулирована клавиша: {key}")

                # Ожидание следующего цикла
                time.sleep(interval)

            except KeyboardInterrupt:
                log("Прерывание пользователем", "info")
                break

            except Exception as e:
                log(f"Критическая ошибка: {str(e)}", "error")
                time.sleep(5)  # Задержка перед повтором

    finally:
        log("Остановка Anti-AFK сервиса")


if __name__ == "__main__":
    if "--service" in sys.argv:
        run_antiafk()
    else:
        print("Для запуска сервиса используйте флаг --service")