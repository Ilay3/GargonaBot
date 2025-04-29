import cv2
import numpy as np
import pyautogui
import time
import sys
import os
import traceback
from datetime import datetime
import platform
import json

sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__








def run_koleso(threshold=0.75, check_interval=1, screenshot_dir="screenshots", result_check_attempts=10):
    print("=" * 40)
    print("Запуск Koleso сервиса")
    print(f"Threshold: {threshold}")
    print(f"Check interval: {check_interval}")
    print("=" * 40)
    # Добавляем путь к корню проекта для корректного импорта
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Инициализируем переменную telegram_enabled
    telegram_enabled = False  # <-- Добавлено здесь

    try:
        from main import send_screenshot_to_telegram
        telegram_enabled = True  # <-- Устанавливаем True при успешном импорте
    except ImportError:
        telegram_enabled = False
        print("Telegram интеграция отключена")
    except Exception as e:
        print(f"Ошибка импорта Telegram: {str(e)}")
        telegram_enabled = False
    if platform.system() != "Windows":
        print("Windows required!")
        return

    pyautogui.FAILSAFE = False

    def load_templates():
        """Загрузка шаблонов изображений с корректными путями для krutkakoles"""
        try:
            if getattr(sys, 'frozen', False):
                base_dir = sys._MEIPASS
                resources_path = os.path.join(base_dir, 'resources', 'images', 'ImgKoleso')
            else:
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
                resources_path = os.path.join(base_dir, 'resources', 'images', 'ImgKoleso')

            print(f"[DEBUG] Resources path: {resources_path}")

            if not os.path.exists(resources_path):
                raise FileNotFoundError(f"Resources directory not found: {resources_path}")

            template_files = {
                "DostupKoleso": "DostupKoleso.png",
                "IconCasino": "IconCasino.png",
                "InterfaceKolesa": "InterfaceKolesa.png",
                "ButtonKoloso": "ButtonKoloso.png",
                "ResultKoleso": "ResultKoleso.png"
            }

            loaded_templates = {}
            for name, filename in template_files.items():
                full_path = os.path.join(resources_path, filename)
                print(f"Загрузка шаблона {name} из {full_path}")
                img = cv2.imread(full_path, 0)
                if img is None:
                    print(f"[ERROR] Не удалось загрузить: {full_path}")
                    raise FileNotFoundError(f"Image not found: {full_path}")
                loaded_templates[name] = img
                print(f"Шаблон {name} загружен")

            return loaded_templates
        except Exception as e:
            print(f"Ошибка загрузки шаблонов: {str(e)}")
            traceback.print_exc()
            return None

    templates = load_templates()
    if not templates:
        print("Не удалось загрузить шаблоны. Выход.")
        return

    def find_template(template_name, threshold=threshold):
        try:
            print(f"Поиск шаблона: {template_name}")
            if template_name not in templates:
                print(f"Шаблон {template_name} не найден в словаре")
                return None

            template = templates[template_name]
            screenshot = pyautogui.screenshot()
            gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2GRAY)

            res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            print(f"Совпадение: {max_val:.2f} (требуется >= {threshold})")
            if max_val >= threshold:
                x, y = max_loc
                center_x = x + template.shape[1] // 2
                center_y = y + template.shape[0] // 2
                print(f"Найдено: ({center_x}, {center_y})")
                return (center_x, center_y)
            print("Шаблон не найден")
            return None
        except Exception as e:
            print(f"Ошибка поиска шаблона: {str(e)}")
            traceback.print_exc()
            return None

    def safe_click(x, y, duration=0.2):
        try:
            print(f"Клик по ({x}, {y})")
            pyautogui.moveTo(x, y, duration=duration)
            pyautogui.click()
            return True
        except Exception as e:
            print(f"Ошибка клика: {str(e)}")
            return False

    def process_step(template_name, action, attempts=5):
        for attempt in range(attempts):
            pos = find_template(template_name)
            if pos:
                if action(pos):
                    return True
            time.sleep(5)
        return False

    try:
        while True:
            try:
                if process_step("DostupKoleso", lambda pos: (
                        time.sleep(65),
                        pyautogui.press('up')
                )):
                    for step in ["IconCasino", "InterfaceKolesa"]:
                        if not process_step(step, lambda pos: safe_click(*pos)):
                            break

                    if process_step("ButtonKoloso", lambda pos: safe_click(*pos)):
                        if process_step("ResultKoleso",
                                        lambda pos: True,
                                        attempts=result_check_attempts):
                            # Добавляем задержку для стабилизации интерфейса
                            time.sleep(3)

                            # Создаем папку с абсолютным путем
                            screenshot_dir_abs = os.path.abspath(screenshot_dir)
                            os.makedirs(screenshot_dir_abs, exist_ok=True)

                            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                            screenshot_path = os.path.join(
                                screenshot_dir_abs,
                                f"koleso_{timestamp}.png"
                            )

                            try:
                                # Делаем скриншот с проверкой
                                pyautogui.screenshot(screenshot_path)
                                print(f"Скриншот сохранен: {screenshot_path}")

                                if telegram_enabled:
                                    # Проверяем существование файла перед отправкой
                                    if os.path.exists(screenshot_path):
                                        print(f"Размер файла: {os.path.getsize(screenshot_path) / 1024:.2f} KB")

                                        # Пытаемся отправить с повторными попытками
                                        success = False
                                        for retry in range(3):
                                            try:
                                                success = send_screenshot_to_telegram(
                                                    screenshot_path,
                                                    caption="Результат колеса удачи:"
                                                )
                                                if success: break
                                                time.sleep(2)
                                            except Exception as tg_error:
                                                print(f"Ошибка Telegram (попытка {retry + 1}): {str(tg_error)}")

                                        # Удаляем только при успешной отправке
                                        if success:
                                            print("Успешно отправлено, удаляю файл")
                                            os.remove(screenshot_path)
                                        else:
                                            print("Не удалось отправить, оставляю файл")
                                            error_path = os.path.join(
                                                screenshot_dir_abs,
                                                f"ERROR_{timestamp}.png"
                                            )
                                            os.rename(screenshot_path, error_path)
                                    else:
                                        print("Ошибка: скриншот не создан!")

                            except Exception as screenshot_error:
                                print(f"Ошибка создания скриншота: {str(screenshot_error)}")
                                traceback.print_exc()

                            time.sleep(20)
                            pyautogui.press('esc')
                            time.sleep(1)
                            pyautogui.press('esc')
                            pyautogui.press('backspace')

                time.sleep(check_interval)

            except KeyboardInterrupt:
                print("Остановлено пользователем")
                break

            except Exception as e:
                print(f"Ошибка в основном цикле: {str(e)}")
                traceback.print_exc()
                time.sleep(5)

    finally:
        print("Сервис колеса остановлен")

if __name__ == "__main__":
    if "--service=koleso" in sys.argv:
        run_koleso()
    else:
        print("Привет")