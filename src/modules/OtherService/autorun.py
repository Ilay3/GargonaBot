import time
import logging
import pydirectinput
import keyboard  # Для отслеживания нажатия клавиш

# Настройка логирования
logging.basicConfig(
    filename='../../../logs/autoran.txt',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

logging.info("Запуск программы для эмуляции зажатия клавиш (autorun).")

# Флаги состояния
emulation_active = False  # Эмуляция клавиш не активна изначально
plus_pressed = False      # Флаг для debounce клавиши '+'

# Главный цикл эмуляции
while True:
    try:
        # Если нажата клавиша '+' и ранее она не была нажата (debounce)
        if keyboard.is_pressed('+'):
            if not plus_pressed:
                plus_pressed = True
                # Переключаем состояние эмуляции
                emulation_active = not emulation_active
                if emulation_active:
                    logging.info("Эмуляция активирована: зажимаем 'w' и 'shift'.")
                    pydirectinput.keyDown('w')
                    pydirectinput.keyDown('shift')
                    print("Эмуляция включена: зажаты 'w' и 'shift'.")
                else:
                    logging.info("Эмуляция деактивирована: отпускаем 'w' и 'shift'.")
                    pydirectinput.keyUp('w')
                    pydirectinput.keyUp('shift')
                    print("Эмуляция отключена: отпущены 'w' и 'shift'.")
        else:
            plus_pressed = False  # Сбрасываем флаг, когда '+' отпущена

        # Небольшая задержка для стабильности работы
        time.sleep(0.1)

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        print(f"Произошла ошибка: {e}")
        break

logging.info("Завершение программы.")
