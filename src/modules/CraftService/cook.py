import cv2
import numpy as np
import pyautogui
import time
import keyboard

templates = {
    "Vegetables": cv2.imread('../../../resources/images/ImgCook/Vegetables.png', 0),
    "Knife": cv2.imread('../../../resources/images/ImgCook/Knife.png', 0),
    "StartCook": cv2.imread('../../../resources/images/ImgCook/StartCook.png', 0),
}

move_positions = {
    "Vegetables": (684, 289),
    "Knife": (811, 298),
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

for _ in range(num_dishes):
    if keyboard.is_pressed('0'):
        print("Остановка программы.")
        break
    print(f"Начинаем готовить {_ + 1}-е блюдо...")
    while True:
        if keyboard.is_pressed('0'):
            print("Остановка программы.")
            break
        time.sleep(1)
        pos1 = find_template_on_screen(templates["Vegetables"])
        if pos1:
            x, y = pos1
            if "Vegetables" in move_positions:
                new_x, new_y = move_positions["Vegetables"]
                pyautogui.moveTo(x, y, duration=0.5)
                pyautogui.dragTo(new_x, new_y, duration=0.5)
                print(f"Перемещено Vegetables.png в {new_x}, {new_y}")
            time.sleep(2)  # Пауза 10 секунд после перемещения test3
            break
        else:
            print("Первая картинка не найдена, продолжаем поиск...")
    for step in ["Knife", "StartCook"]:
        while True:
            if keyboard.is_pressed('0'):
                print("Остановка программы.")
                break
            time.sleep(1)
            pos = find_template_on_screen(templates[step])
            if pos:
                x, y = pos
                if step in move_positions:
                    new_x, new_y = move_positions[step]
                    pyautogui.moveTo(x, y, duration=0.5)
                    pyautogui.dragTo(new_x, new_y, duration=0.5)
                    print(f"Перемещено {step}.png в {new_x}, {new_y}")
                pyautogui.click(x, y)
                print(f"Клик по {step}.png в координатах: {x}, {y}")
                break
            else:
                print(f"{step}.png не найден, продолжаем поиск...")
    time.sleep(8)

print("Все блюда приготовлены!")
