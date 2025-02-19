import os
import sys
import cv2
import numpy as np
import pyautogui
import time
import keyboard

pyautogui.FAILSAFE = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(BASE_DIR, "..", "..", "..", "resources", "images", "ImgCook")

# Список блюд и их изображения
menu = {
    "Салат": ["Vegetables.png", "Knife.png", "StartCook.png"],
    "Смузи": ["Vegetables.png", "Water.png", "Venchik.png", "StartCook.png"],
    "Рагу": ["Meat.png", "Water.png","Vegetables.png","Fire.png", "StartCook.png"]
}

# Выбор блюда
print("Выберите блюдо:")
for i, dish in enumerate(menu.keys(), start=1):
    print(f"{i}. {dish}")

dish_choice = int(input("Введите номер блюда: ")) - 1
selected_dish = list(menu.keys())[dish_choice]

templates = {name: cv2.imread(os.path.join(RESOURCES_DIR, name), 0) for name in menu[selected_dish]}

move_positions = {
    "Vegetables.png": (684, 289), "Knife.png": (811, 298),  "StartCook.png": (812, 671),
    "Vegetables.png": (684, 289), "Water.png": (811, 298), "Venchik.png":(930, 299),  "StartCook.png": (812, 671),
    "Vegetables.png": (684, 289), "Water.png": (811, 298),"Meat.png": (930, 299), "Fire.png": (672, 419),  "StartCook.png": (812, 671),
}


def find_template_on_screen(template, threshold=0.9):
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    if len(loc[0]) > 0:
        y, x = loc[0][0], loc[1][0]
        return x + template.shape[1] // 2, y + template.shape[0] // 2
    return None


num_dishes = int(input("Сколько блюд нужно приготовить? "))

for i in range(num_dishes):
    if keyboard.is_pressed('0'):
        print("Остановка программы.")
        break
    print(f"Начинаем готовить {i + 1}-е блюдо ({selected_dish})...")

    for step in menu[selected_dish]:
        while not keyboard.is_pressed('0'):
            time.sleep(1)
            pos = find_template_on_screen(templates[step])
            if pos:
                x, y = pos
                if step in move_positions:
                    new_x, new_y = move_positions[step]
                    pyautogui.moveTo(x, y, duration=0.5)
                    pyautogui.dragTo(new_x, new_y, duration=0.5)
                    print(f"Перемещено {step} в {new_x}, {new_y}")
                pyautogui.click(x, y)
                print(f"Клик по {step} в координатах: {x}, {y}")
                break
            else:
                print(f"{step} не найден, продолжаем поиск...")
    time.sleep(8)

print("Все блюда приготовлены!")
