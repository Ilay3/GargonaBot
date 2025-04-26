import pyautogui
import numpy as np
import cv2
import time
import sys
from datetime import datetime
from collections import Counter
import traceback

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
    x, y, w, h = calculate_region(points)
    screenshot = pyautogui.screenshot(region=(x, y, w, h))
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(img, lower, upper)
    return np.any(mask > 0)

def run_color_detection(zones_config, key_map, stop_config, check_interval=1/32):
    pyautogui.FAILSAFE = False
    last_exception = None
    exception_count = 0

    try:
        while True:
            try:
                # Проверка STOP-зоны
                stop_active = check_stop_area(stop_config['points'],
                                            stop_config['lower'],
                                            stop_config['upper'])

                if stop_active:
                    time.sleep(7)
                    continue

                # Основной цикл проверки
                for zone_name, config in zones_config.items():
                    try:
                        points, target_color = config
                        region = calculate_region(points)

                        screenshot = pyautogui.screenshot(region=region)
                        img = np.array(screenshot)
                        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

                        dominant_color = get_dominant_color(img)
                        hex_color = '#{:02x}{:02x}{:02x}'.format(*dominant_color)

                        if hex_color.lower() == target_color.lower():
                            pyautogui.press(key_map[zone_name])
                            time.sleep(1/8)

                    except Exception as zone_error:
                        traceback.print_exc()

                time.sleep(check_interval)
                exception_count = 0

            except Exception as main_loop_error:
                exception_count += 1
                traceback.print_exc()
                if exception_count > 5:
                    break
                time.sleep(1)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    zones_config = {
        "A": ([(843, 833), (843, 917), (929, 833), (929, 917)], "#0000ff"),
        "D": ([(992, 830), (992, 916), (1077, 830), (1077, 916)], "#0000ff")
    }

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