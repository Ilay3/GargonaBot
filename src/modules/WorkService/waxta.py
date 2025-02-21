import cv2
import numpy as np
import pyautogui
import time
import sys


def template_matching_service(image_path, key_to_press='e', threshold=0.9, check_interval=1 / 32):
    """
    Запускает сервисный процесс поиска шаблона на экране и нажатия клавиши при обнаружении.

    :param image_path: Путь к эталонному изображению.
    :param key_to_press: Клавиша, которую нужно нажимать при обнаружении.
    :param threshold: Порог совпадения шаблона.
    :param check_interval: Интервал проверки экрана.
    """
    pyautogui.FAILSAFE = False
    template = cv2.imread(image_path, 0)

    if template is None:
        print(f"Ошибка: не удалось загрузить изображение {image_path}")
        return

    def find_template_on_screen():
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        res = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)
        return len(loc[0]) > 0

    print("Сервис запущен...")
    while True:
        if find_template_on_screen():
            while find_template_on_screen():
                pyautogui.press(key_to_press)
                print(f"Обнаружено {image_path}, нажата клавиша {key_to_press}")
                time.sleep(check_interval)
        time.sleep(1)


if __name__ == "__main__":
    if "--service" in sys.argv:
        template_matching_service('../../../resources/images/ImgWaxta/ButtonE.png')
    else:
        print("Флаг --service не передан, выход из программы.")
