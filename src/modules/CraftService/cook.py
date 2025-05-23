import os
import sys
import cv2
import numpy as np
import pyautogui
import time
import keyboard
import argparse
import easyocr


def get_resource_path(relative_path):
    try:
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    except Exception:
        raise


def run_cookbot():
    try:
        reader = easyocr.Reader(['ru'])

        parser = argparse.ArgumentParser()
        parser.add_argument("script", nargs='?', help=argparse.SUPPRESS)
        parser.add_argument("--service", type=str, required=True)
        parser.add_argument("--dish", type=str, required=True)
        parser.add_argument("--quantity", type=int, required=True)

        args = parser.parse_args()

        if args.service != "cookbot":
            return

        paths = {
            "Vegetables": get_resource_path("resources/images/ImgCook/Vegetables.png"),
            "Knife": get_resource_path("resources/images/ImgCook/Knife.png"),
            "Water": get_resource_path("resources/images/ImgCook/Water.png"),
            "Venchik": get_resource_path("resources/images/ImgCook/Venchik.png"),
            "Meat": get_resource_path("resources/images/ImgCook/Meat.png"),
            "Fire": get_resource_path("resources/images/ImgCook/Fire.png")
        }

        templates = {}
        for name, path in paths.items():
            template = cv2.imread(path, 0)
            if template is None:
                return
            templates[name] = template

        menu_config = {
            "Салат": ["Vegetables", "Knife", "StartCook"],
            "Смузи": ["Vegetables", "Water", "Venchik", "StartCook"],
            "Рагу": ["Meat", "Water", "Vegetables", "Fire", "StartCook"]
        }

        move_positions = {
            "Салат": {"Vegetables": (684, 289), "Knife": (811, 298), "StartCook": (812, 671)},
            "Смузи": {"Vegetables": (684, 289), "Water": (811, 298), "Venchik": (930, 299), "StartCook": (812, 671)},
            "Рагу": {"Meat": (930, 299), "Water": (811, 298), "Vegetables": (684, 289), "Fire": (672, 419),
                     "StartCook": (812, 671)}
        }

        if args.dish not in menu_config:
            return

        pyautogui.FAILSAFE = False

        for i in range(args.quantity):
            if keyboard.is_pressed('0'):
                return

            for step in menu_config[args.dish]:
                found = False

                if step == "StartCook":
                    target_text = "Начать Готовку"
                    for attempt in range(10):
                        try:
                            screenshot = pyautogui.screenshot()
                            img = np.array(screenshot)
                            results = reader.readtext(img, detail=1, paragraph=False)

                            for (bbox, text, prob) in results:
                                if target_text.lower() in text.lower() and prob > 0.3:
                                    top_left = tuple(map(int, bbox[0]))
                                    bottom_right = tuple(map(int, bbox[2]))
                                    x_center = (top_left[0] + bottom_right[0]) // 2
                                    y_center = (top_left[1] + bottom_right[1]) // 2
                                    pyautogui.click(x_center, y_center)
                                    found = True
                                    break
                            if found:
                                break
                            time.sleep(0.5)
                        except Exception:
                            pass
                    if not found:
                        return

                else:
                    template = templates[step]
                    for attempt in range(10):
                        try:
                            screenshot = pyautogui.screenshot()
                            gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
                            res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
                            _, max_val, _, max_loc = cv2.minMaxLoc(res)

                            if max_val >= 0.9:
                                x = max_loc[0] + template.shape[1] // 2
                                y = max_loc[1] + template.shape[0] // 2

                                if step in move_positions[args.dish]:
                                    new_x, new_y = move_positions[args.dish][step]
                                    pyautogui.moveTo(x, y, duration=0.3)
                                    pyautogui.dragTo(new_x, new_y, duration=0.5, button='left')

                                pyautogui.click(x, y)
                                found = True
                                break
                        except Exception:
                            pass
                        time.sleep(0.5)

                if not found:
                    return

                time.sleep(1)

            time.sleep(8)

    except Exception:
        pass


if __name__ == "__main__":
    run_cookbot()