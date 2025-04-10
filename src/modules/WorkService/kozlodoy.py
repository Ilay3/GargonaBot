import pyautogui
import numpy as np
import cv2
import time
import logging
import sys
from datetime import datetime
from collections import Counter
import traceback

def log(message, level="info"):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    if level == "info":
        logging.info(log_message)
    elif level == "error":
        logging.error(log_message)


def get_dominant_color(image):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    pixels = hsv_image.reshape(-1, 3)
    colors = [tuple(pixel) for pixel in pixels]
    color_counts = Counter(colors)
    return color_counts.most_common(1)[0][0]


def calculate_region(points):
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    return (min(x_coords), min(y_coords), max(x_coords) - min(x_coords), max(y_coords) - min(y_coords))


def check_stop_area(points, lower, upper):
    """Проверяет наличие цвета в STOP-зоне"""
    x, y, w, h = calculate_region(points)
    screenshot = pyautogui.screenshot(region=(x, y, w, h))
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(img, lower, upper)
    return np.any(mask > 0)


def run_color_detection(zones_config, key_map, stop_config, check_interval=1/32):
    # Настройка логгера
    service_logger = logging.getLogger('KozlodoyService')
    service_logger.setLevel(logging.DEBUG)

    # Обработчик для сервиса
    fh = logging.FileHandler('kozlodoy_service.log', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    service_logger.addHandler(fh)

    service_logger.info("Сервис запущен")
    service_logger.debug(f"Конфигурация: {zones_config}")
    service_logger.debug(f"Клавиши: {key_map}")
    service_logger.debug(f"Стоп-зона: {stop_config}")

    pyautogui.FAILSAFE = False
    last_exception = None
    exception_count = 0

    try:
        while True:
            try:
                # Логирование состояния
                if datetime.now().second % 30 == 0:  # Каждые 30 секунд
                    service_logger.info(f"Работает. Исключений: {exception_count}")

                # Проверка STOP-зоны
                stop_check_start = time.time()
                stop_active = check_stop_area(stop_config['points'],
                                              stop_config['lower'],
                                              stop_config['upper'])
                service_logger.debug(f"Проверка стоп-зоны: {stop_active} Время: {time.time() - stop_check_start:.3f}с")

                if stop_active:
                    service_logger.warning("Обнаружена стоп-зона! Пауза 5.5с")
                    time.sleep(7)
                    continue

                # Основной цикл проверки
                for zone_name, config in zones_config.items():
                    try:
                        points, target_color = config
                        region = calculate_region(points)
                        service_logger.debug(f"Проверка зоны {zone_name} в регионе {region}")

                        screenshot_start = time.time()
                        screenshot = pyautogui.screenshot(region=region)
                        service_logger.debug(f"Скриншот сделан за {time.time() - screenshot_start:.3f}с")

                        img = np.array(screenshot)
                        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

                        color_start = time.time()
                        dominant_color = get_dominant_color(img)
                        hex_color = '#{:02x}{:02x}{:02x}'.format(*dominant_color)
                        service_logger.debug(
                            f"Цвет: {hex_color} vs целевой {target_color} Время: {time.time() - color_start:.3f}с")

                        if hex_color.lower() == target_color.lower():
                            service_logger.info(f"Нажатие {key_map[zone_name]}")
                            pyautogui.press(key_map[zone_name])
                            time.sleep(1/8)

                    except Exception as zone_error:
                        service_logger.error(f"Ошибка в зоне {zone_name}: {str(zone_error)}")
                        traceback.print_exc()

                time.sleep(check_interval)
                exception_count = 0

            except Exception as main_loop_error:
                exception_count += 1
                service_logger.error(f"Ошибка в основном цикле ({exception_count}): {str(main_loop_error)}")
                traceback.print_exc()
                if exception_count > 5:
                    service_logger.critical("Слишком много ошибок. Аварийное завершение")
                    break
                time.sleep(1)

    except KeyboardInterrupt:
        service_logger.warning("Прерывание пользователем")
    except Exception as e:
        service_logger.critical(f"Критическая ошибка: {str(e)}")
        traceback.print_exc()
    finally:
        service_logger.info("Сервис остановлен")

if __name__ == "__main__":
    # Конфигурация зон
    zones_config = {
        "A": ([(843, 833), (843, 917), (929, 833), (929, 917)], "#0000ff"),
        "D": ([(992, 830), (992, 916), (1077, 830), (1077, 916)], "#0000ff")
    }

    # Конфигурация STOP-зоны (красный цвет в HSV)
    stop_config = {
        'points': [(1203, 535), (1236, 535), (1203, 854), (1236, 854)],
        'lower': np.array([0, 100, 100]),
        'upper': np.array([10, 255, 255])
    }

    key_map = {"A": "a", "D": "d"}

    if "--service=kozlodoy" in sys.argv:
        run_color_detection(zones_config, key_map, stop_config)
    else:
        print("Флаг --service= не найден. Завершение.")