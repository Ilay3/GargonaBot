import sys
import os
import ctypes
import json
import datetime
import requests
import subprocess
import uuid
import platform
import hashlib
import threading
import time
import numpy as np
import traceback

from PySide6.QtWidgets import QInputDialog, QMessageBox

def authenticate():
    """
    Спрашивает у пользователя лицензионный ключ и проверяет его на сервере.
    Если ключ валиден — сохраняет локально и возвращает дату истечения.
    В противном случае повторяет ввод.
    """
    while True:
        # Открываем диалог для ввода ключа
        key, ok = QInputDialog.getText(None, "Авторизация", "Введите лицензионный ключ:")
        if not ok:
            # Пользователь отменил ввод — завершаем приложение
            sys.exit(1)

        # Отправляем ключ на сервер
        success, expiry = validate_key(key)
        if success:
            # Сохраняем локально и возвращаем дату окончания
            save_license(key, expiry)
            return expiry

        # Если неуспешно — предупреждаем и цикл повторяется
        QMessageBox.warning(
            None,
            "Ошибка лицензии",
            "Неверный ключ или срок истёк.\nПопробуйте ещё раз."
        )

PYTHON_EXEC = sys.executable


def send_screenshot_to_telegram(screenshot_path, message=None,caption=None):
    from datetime import datetime
    print(f"\n[Telegram] Начало отправки: {datetime.now().isoformat()}")
    print(f"[Telegram] Проверка файла: {screenshot_path}")

    try:
        if not os.path.exists(screenshot_path):
            print(f"[ERROR] Файл не существует: {screenshot_path}")
            return False
        print(f"\n[Telegram] Попытка отправки: {os.path.basename(screenshot_path)}")
        print(f"[Telegram] Абсолютный путь: {os.path.abspath(screenshot_path)}")
        print(f"[Telegram] Файл существует: {os.path.exists(screenshot_path)}")
        print(f"[Telegram] Размер файла: {os.path.getsize(screenshot_path)} bytes")

        # Загрузка настроек
        settings_path = os.path.join(os.path.dirname(__file__), '..', 'settings.json')
        print(f"[Telegram] Путь к настройкам: {settings_path}")

        with open(settings_path, "r") as f:
            settings = json.load(f)

        token = settings.get("telegram_token")
        chat_id = settings.get("telegram_chat_id")

        if not token or not chat_id:
            print("[ERROR] Отсутствуют токен или chat_id")
            return False

        print(f"[Telegram] Используется токен: {token[:3]}...{token[-2:]}")
        print(f"[Telegram] Используется chat_id: {chat_id}")

        # Отправка запроса
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        files = {'photo': open(screenshot_path, 'rb')}
        data = {'chat_id': chat_id, 'caption': message}

        print(f"[Telegram] Отправка запроса: {url}")
        response = requests.post(url, files=files, data=data, timeout=10)

        print(f"[Telegram] Ответ сервера: {response.status_code}")
        print(f"[Telegram] Содержимое ответа: {response.text}")

        return response.status_code == 200

    except Exception as e:
        print(f"[Telegram ERROR] {str(e)}")
        traceback.print_exc()
        return False


def run_service_mode():
    print("Запуск сервисного режима!")
    for arg in sys.argv[1:]:
        print("Аргумент:", arg)
        if arg.startswith("--service="):
            service_name = arg.split("=")[1]
            print("Сервис:", service_name)


            if service_name == "antiafk":

                from modules.AntiAfkService.antiafk import run_antiafk
                run_antiafk()
                sys.exit(0)
            elif service_name == "lottery":

                print("[DEBUG][main1] Starting lottery service...")
                try:
                    from modules.AntiAfkService.lottery import run_lottery_service
                    print("[DEBUG][main1] Module imported successfully")
                    run_lottery_service()
                    print("[DEBUG][main1] Service finished")
                except Exception as e:
                    print(f"[ERROR][main1] Failed to run service: {str(e)}")
                    traceback.print_exc()
                sys.exit(0)

            elif service_name == "waxta":
                from modules.WorkService.waxta import run_waxta


                run_waxta()
                sys.exit(0)
            elif service_name == "port":
                from modules.WorkService.port import run_port

                run_port()
                sys.exit(0)
            elif service_name == "stroyka":

                from modules.WorkService.stroyka import run_stroyka


                try:
                    run_stroyka()
                except Exception as e:

                    traceback.print_exc()


                sys.exit(0)
            elif service_name == "kozlodoy":
                from modules.WorkService.kozlodoy import run_color_detection
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
                run_color_detection(zones_config, key_map, stop_config)
                sys.exit(0)
            elif service_name == "autoeat":
                from modules.OtherService.autoeat import run_autoeat

                run_autoeat()
                sys.exit(0)
            elif service_name == "automood":
                from modules.OtherService.automood import run_automood

                run_automood()
                sys.exit(0)
            elif service_name == "autorun":
                from modules.OtherService.autorun import run_autorun

                run_autorun()
                sys.exit(0)
            elif service_name == "kachalka":
                from modules.OtherService.kachalka import run_kachalka

                run_kachalka()
                sys.exit(0)
            elif service_name == "cookbot":
                from modules.CraftService.cook import run_cookbot

                run_cookbot()
                sys.exit(0)
            elif service_name == "kosyaki":
                from modules.CraftService.kosyaki import run_kosyaki

                run_kosyaki()
                sys.exit(0)
            elif service_name == "taxi":
                from modules.WorkService.Taxi import run_taxi

                run_taxi()
                sys.exit(0)
            elif service_name == "schems":
                from modules.MiniGamesService.Schems import run_schemas

                run_schemas()
                sys.exit(0)
            elif service_name == "shveika":
                print("main.py: Ветка service_name == 'shveika' активна")
                from modules.MiniGamesService.Shveika import run_shveika
                run_shveika()
                sys.exit(0)
            elif service_name == "skolzkaya":
                from modules.MiniGamesService.Skolzkaya import run_Skolzkaya

                run_Skolzkaya()
                sys.exit(0)
            elif service_name == "koleso":
                from modules.AntiAfkService.krutkakoles import run_koleso
                run_koleso()
                sys.exit(0)
            elif service_name == "demorgan":
                from modules.TuragaService.ShveiaDemorgan import run_shveia_demorgan

                run_shveia_demorgan()
                sys.exit(0)
            elif service_name == "tochilka":
                from modules.TuragaService.Tochilka import run_tochilka

                run_tochilka()
                sys.exit(0)

    sys.exit(0)

# Если передан флаг сервисного режима – запускаем его и выходим

if any(arg.startswith("--service=") for arg in sys.argv[1:]):
    run_service_mode()
from telegram import Update, ParseMode, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, Filters, Updater


from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QStackedWidget, QPushButton, QLabel, QLineEdit, QCheckBox,
    QDialog, QSizePolicy, QMessageBox, QComboBox
)



SERVER_URL = "http://2.56.89.210:5000/"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.isdir(os.path.join(BASE_DIR, "src")):
    PROJECT_ROOT = BASE_DIR
else:
    PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

LICENSE_FILE = os.path.join(PROJECT_ROOT, "license.dat")
SETTINGS_FILE = os.path.join(PROJECT_ROOT, "settings.json")
print(f"Используется файл настроек: {SETTINGS_FILE}")

def get_keyboard_layout():
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    hwnd = user32.GetForegroundWindow()
    thread_id = user32.GetWindowThreadProcessId(hwnd, None)
    layout_id = user32.GetKeyboardLayout(thread_id)
    return layout_id & 0xFFFF

LANG_ENGLISH = 0x0409

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
    return {}

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)
    print("Настройки сохранены.")

MODULES_BASE = None
if os.path.isdir(os.path.join(BASE_DIR, "modules")):
    MODULES_BASE = os.path.join(BASE_DIR, "modules")
elif os.path.isdir(os.path.join(BASE_DIR, "src", "modules")):
    MODULES_BASE = os.path.join(BASE_DIR, "src", "modules")
else:
    raise FileNotFoundError("Не найдена папка modules")

sys.path.append(os.path.join(MODULES_BASE, "ProcessChecker"))
import process_checker

# Пути к скриптам
ANTIAFK_PATH     = os.path.join(MODULES_BASE, "AntiAfkService", "antiafk.py")
KRUTKAKOLES_PATH = os.path.join(MODULES_BASE, "AntiAfkService", "krutkakoles.py")
LOTTERY_PATH     = os.path.join(MODULES_BASE, "AntiAfkService", "lottery.py")
COOK_PATH        = os.path.join(MODULES_BASE, "CraftService", "cook.py")
WAXTA_PATH       = os.path.join(MODULES_BASE, "WorkService", "waxta.py")
PORT_PATH        = os.path.join(MODULES_BASE, "WorkService", "port.py")
STROYKA_PATH     = os.path.join(MODULES_BASE, "WorkService", "stroyka.py")
KOZLODOY_PATH    = os.path.join(MODULES_BASE, "WorkService", "kozlodoy.py")
AUTORUN_PATH     = os.path.join(MODULES_BASE, "OtherService", "autorun.py")
AUTOMOOD_PATH    = os.path.join(MODULES_BASE, "OtherService", "automood.py")
AUTOEAT_PATH     = os.path.join(MODULES_BASE, "OtherService", "autoeat.py")
KACHALKA_PATH    = os.path.join(MODULES_BASE, "OtherService", "kachalka.py")
KOSYAKI_PATH     = os.path.join(MODULES_BASE, "CraftService", "kosyaki.py")
TAXI_PATH        = os.path.join(MODULES_BASE, "WorkService", "Taxi.py")
FIREMAN_PATH     = os.path.join(MODULES_BASE, "WorkService", "fireman.py")
SHVEIKA_PATH     = os.path.join(MODULES_BASE, "MiniGamesService", "Shveika.py")
SKOLZKAYA_PATH   = os.path.join(MODULES_BASE, "MiniGamesService", "Skolzkaya.py")
SCHEMS_PATH      = os.path.join(MODULES_BASE, "MiniGamesService", "Schems.py")
RECONNECT_PATH   = os.path.join(MODULES_BASE, "OtherService", "reconect.py")
DEMORGAN_PATH    = os.path.join(MODULES_BASE, "TuragaService", "ShveiaDemorgan.py")
TOCHILKA_PATH    = os.path.join(MODULES_BASE, "TuragaService", "Tochilka.py")
FULLRECONNECT_PATH= os.path.join(MODULES_BASE, "OtherService", "fullreconect.py")
PYTHON_EXEC = sys.executable

def get_device_id():
    return hex(uuid.getnode())

def get_hwid():
    mac = str(uuid.getnode())
    computer_name = os.environ.get('COMPUTERNAME', 'unknown')
    processor = platform.processor()
    combined = mac + computer_name + processor
    return hashlib.sha256(combined.encode()).hexdigest()

def validate_key(key: str):
    hwid = get_hwid()
    print(f" Отправляем на сервер:\n  Ключ: {key}\n  HWID: {hwid}")
    try:
        response = requests.post(f"{SERVER_URL}/validate", json={"key": key, "hwid": hwid})
        data = response.json()
        print(f" Ответ сервера: {data}")
        if response.status_code == 200:
            expiry_date_str = data.get("expiry_date")
            expiry_date = datetime.datetime.strptime(expiry_date_str, "%Y-%m-%d %H:%M:%S")
            print(f" Ключ действителен. Подписка до {expiry_date}")
            return True, expiry_date
        else:
            print(f"❌ Ошибка: {data.get('message', 'Unknown error')}")
            return False, None
    except requests.RequestException as e:
        print(f" Ошибка подключения к серверу: {e}")
        return False, None

def load_license():
    if os.path.exists(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, "r") as f:
                license_info = json.load(f)
            stored_hwid = license_info.get("hwid")
            current_hwid = get_hwid()
            if stored_hwid != current_hwid:
                print(" HWID не совпадает! Требуется повторная активация.")
                return None
            expiry_date_str = license_info.get("expiry_date")
            if expiry_date_str:
                return datetime.datetime.strptime(expiry_date_str, "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(f" Ошибка загрузки лицензии: {e}")
    return None

def save_license(key, expiry_date):
    license_info = {
        "key": key,
        "hwid": get_hwid(),
        "expiry_date": expiry_date.strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        with open(LICENSE_FILE, "w") as f:
            json.dump(license_info, f)
        print(f"Лицензия сохранена: подписка до {expiry_date}")
    except Exception as e:
        print(f" Ошибка при сохранении лицензии: {e}")



class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.launch_game_button = None
        self.setWindowTitle("Менеджер сервисов бота")
        self.setGeometry(100, 100, 900, 600)
        self.telegram_bot_enabled = False
        # Обновлённый словарь процессов
        self.processes = {
            "antiafk": None,
            "koleso": None,
            "lottery": None,
            "cook": None,
            "waxta": None,
            "port": None,
            "stroyka": None,
            "kozlodoy": None,
            "autorun": None,
            "automood": None,
            "autoeat": None,
            "kachalka": None,
            "kosyaki": None,
            "taxi": None,
            "fireman": None,
            "shveika": None,
            "skolzkaya": None,
            "telegram_bot": None,
            "schems": None,
            "reconnect": None,
            "fullreconnect": None,
            "demorgan": None,
            "tochilka": None

        }

        self.inactive_counter = 0
        self.bots_killed_due_to_inactivity = False

        self.license_expiry = load_license()

        self.license_check_timer = QTimer(self)
        self.license_check_timer.timeout.connect(self.periodic_license_check)
        self.license_check_timer.start(3600000)

        self.keyboard_timer = QTimer(self)
        self.keyboard_timer.timeout.connect(self.check_keyboard_layout)
        self.keyboard_timer.start(10000)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Создаем левое меню
        left_panel = QWidget()
        left_panel.setSizePolicy(left_panel.sizePolicy().horizontalPolicy(), QSizePolicy.Expanding)
        left_layout = QVBoxLayout(left_panel)
        self.menu_list = QListWidget()
        self.menu_list.setStyleSheet(
            "font-size: 18px;"
            "QListWidget::item:selected { background-color: #ff7043; border: 4px solid #ff7043; }"
        )
        # Обновленный порядок пунктов меню
        self.menu_list.addItem("Начало")
        self.menu_list.addItem("Anti-AFK")
        self.menu_list.addItem("Работы")
        self.menu_list.addItem("Крафты")
        self.menu_list.addItem("Пассивные функции")
        self.menu_list.addItem("Контракты")
        self.menu_list.addItem("Спортзал")
        self.menu_list.addItem("Деморган")
        self.menu_list.addItem("Настройки")
        self.menu_list.addItem("Телеграмм")
        self.menu_list.currentRowChanged.connect(self.switch_page)
        left_layout.addWidget(self.menu_list)

        self.license_label = QLabel()
        self.license_label.setStyleSheet("font-size: 14px; color: #ff7043;")
        left_layout.addWidget(self.license_label)
        left_layout.setAlignment(self.license_label, Qt.AlignBottom)

        main_layout.addWidget(left_panel, 1)

        # Создаем страницы
        self.pages = QStackedWidget()
        self.page_home = self.create_home_page()
        self.page_antiafk = self.create_antiafk_page()
        self.page_work = self.create_work_page()
        self.page_cook = self.create_cook_page()
        self.page_automood = self.create_automood_page()
        self.page_contracts = self.create_contracts_page()
        self.page_sportzal = self.create_sportzal_page()
        self.page_demorgan = self.create_demorgan_page()
        self.page_settings = self.create_settings_page()
        self.tg_page = self.create_tg_page()

        # Добавляем страницы в нужном порядке
        self.pages.addWidget(self.page_home)       # 0: Начало
        self.pages.addWidget(self.page_antiafk)      # 1: Anti-AFK
        self.pages.addWidget(self.page_work)         # 2: Работы
        self.pages.addWidget(self.page_cook)         # 3: Крафты
        self.pages.addWidget(self.page_automood)     # 4: Пассивные функции
        self.pages.addWidget(self.page_contracts)    # 5: Контракты
        self.pages.addWidget(self.page_sportzal)       # 6: Спортзал
        self.pages.addWidget(self.page_demorgan)       # 7: Деморган
        self.pages.addWidget(self.page_settings)       # 8: Настройки
        self.pages.addWidget(self.tg_page)             # 9: Телеграмм

        main_layout.addWidget(self.pages, 3)
        self.switch_page(0)

        self.game_timer = QTimer(self)
        self.game_timer.timeout.connect(self.check_game_active)
        self.game_timer.start(1000)

        self.license_timer = QTimer(self)
        self.license_timer.timeout.connect(self.update_license_label)
        self.license_timer.start(1000)

    def closeEvent(self, event):
        """Вызывается при закрытии окна"""
        self.kill_all_bots()
        event.accept()

    def kill_all_bots(self):
        """Принудительное завершение всех процессов"""
        for name in list(self.processes.keys()):
            proc = self.processes[name]
            if proc is not None:
                try:
                    # Для Windows
                    if os.name == 'nt':
                        subprocess.run(
                            ['taskkill', '/F', '/T', '/PID', str(proc.pid)],
                            shell=True,
                            check=True,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )



                    if proc.poll() is None:
                        proc.wait(timeout=5)

                except Exception as e:
                    print(f"Ошибка при остановке {name}: {e}")
                    traceback.print_exc()
                finally:
                    self.processes[name] = None

        # Сброс всех кнопок в исходное состояние
        self.antiafk_button.setText("Запустить Anti-AFK")
        self.antiafk_button.setStyleSheet("font-size: 16px; padding: 10px;")

        self.chk_koleso.setChecked(False)
        self.chk_lottery.setChecked(False)
        self.chk_myservice.setChecked(False)

        self.waxta_button.setText("Запустить работу на Шахте")
        self.waxta_button.setStyleSheet("font-size: 16px; padding: 10px;")

        self.port_button.setText("Запустить работу в Порту")
        self.port_button.setStyleSheet("font-size: 16px; padding: 10px;")

        self.stroyka_button.setText("Запустить работу на Стройке")
        self.stroyka_button.setStyleSheet("font-size: 16px; padding: 10px;")

        self.kozlodoy_button.setText("Запустить работу на Ферме")
        self.kozlodoy_button.setStyleSheet("font-size: 16px; padding: 10px;")

        self.taxi_button.setText("Запустить работу в Такси")
        self.taxi_button.setStyleSheet("font-size: 16px; padding: 10px;")

        self.chk_autorun.setChecked(False)

        self.cook_button.setText("Запустить")
        self.cook_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.cook_error_label.setText("")

        self.kosyaki_button.setText("Запустить создание Косяков")
        self.kosyaki_button.setStyleSheet("font-size: 16px; padding: 10px;")

        self.automood_launch_button.setText("Запустить Авто-Настроение")
        self.automood_launch_button.setStyleSheet("font-size: 16px; padding: 10px;")

        self.autorun_launch_button.setText("Запустить Авто-Бег")
        self.autorun_launch_button.setStyleSheet("font-size: 16px; padding: 10px;")

        self.autoeat_launch_button.setText("Запустить Авто-Еда")
        self.autoeat_launch_button.setStyleSheet("font-size: 16px; padding: 10px;")

        self.kachalka_launch_button.setText("Запустить тренировку в спортзале")
        self.kachalka_launch_button.setStyleSheet("font-size: 16px; padding: 10px;")

        self.shveika_button.setText("Запустить Швейную фабрику")
        self.shveika_button.setStyleSheet("font-size: 16px; padding: 10px;")

        self.skolzkaya_button.setText("Запустить Скользкая дорога")
        self.skolzkaya_button.setStyleSheet("font-size: 16px; padding: 10px;")

        self.schems_button.setText("Запустить Схемы")
        self.schems_button.setStyleSheet("font-size: 16px; padding: 10px;")

        self.demorgan_button.setText("Запустить Пошив Формы")
        self.demorgan_button.setStyleSheet("font-size: 16px; padding: 10px;")

        self.tochilka_button.setText("Запустить Точилку")
        self.tochilka_button.setStyleSheet("font-size: 16px; padding: 10px;")

        print("Все процессы остановлены, интерфейс сброшен")
    def create_home_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        title = QLabel("Добро пожаловать!")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        description = QLabel("Это менеджер сервисов бота.\nВыберите нужную функцию в меню слева.")
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet("font-size: 18px;")
        layout.addWidget(description)
        layout.addStretch()
        return widget

    def switch_page(self, index):
        self.pages.setCurrentIndex(index)

    def create_antiafk_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        title = QLabel("Anti-AFK")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px;")
        layout.addWidget(title)
        self.antiafk_button = QPushButton("Запустить Anti-AFK")
        self.antiafk_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.antiafk_button.clicked.connect(self.toggle_antiafk)
        layout.addWidget(self.antiafk_button)
        self.chk_koleso = QCheckBox("Колесо-Удачи")
        self.chk_koleso.setStyleSheet("""
            QCheckBox::indicator { width: 15px; height: 15px; }
            QCheckBox::indicator:unchecked { background-color: #bdbdbd; border: 2px solid #757575; border-radius: 7px; }
            QCheckBox::indicator:checked { background-color: #ff7043; border: 2px solid #ffa726; border-radius: 7px; }
            QCheckBox { font-size: 16px; }
        """)
        self.chk_koleso.toggled.connect(self.toggle_koleso)
        layout.addWidget(self.chk_koleso)
        self.chk_lottery = QCheckBox("Лотерея")
        self.chk_lottery.setStyleSheet("""
            QCheckBox::indicator { width: 15px; height: 15px; }
            QCheckBox::indicator:unchecked { background-color: #bdbdbd; border: 2px solid #757575; border-radius: 7px; }
            QCheckBox::indicator:checked { background-color: #ff7043; border: 2px solid #ffa726; border-radius: 7px; }
            QCheckBox { font-size: 16px; }
        """)
        self.chk_lottery.toggled.connect(self.toggle_lottery)
        layout.addWidget(self.chk_lottery)
        self.chk_myservice = QCheckBox("Reconnect")
        self.chk_myservice.setStyleSheet("""
            QCheckBox::indicator { width: 15px; height: 15px; }
            QCheckBox::indicator:unchecked { background-color: #bdbdbd; border: 2px solid #757575; border-radius: 7px; }
            QCheckBox::indicator:checked { background-color: #ff7043; border: 2px solid #ffa726; border-radius: 7px; }
            QCheckBox { font-size: 16px; }
        """)
        self.chk_myservice.toggled.connect(self.toggle_reconnect)
        layout.addWidget(self.chk_myservice)
        layout.addStretch()
        return widget

    def create_work_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        title = QLabel("Работы")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px;")
        layout.addWidget(title)
        self.waxta_button = QPushButton("Запустить работу на Шахте")
        self.waxta_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.waxta_button.clicked.connect(self.toggle_waxta)
        layout.addWidget(self.waxta_button)
        self.port_button = QPushButton("Запустить работу в Порту")
        self.port_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.port_button.clicked.connect(self.toggle_port)
        layout.addWidget(self.port_button)
        self.stroyka_button = QPushButton("Запустить работу на Стройке")
        self.stroyka_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.stroyka_button.clicked.connect(self.toggle_stroyka)
        layout.addWidget(self.stroyka_button)
        self.kozlodoy_button = QPushButton("Запустить работу на Ферме")
        self.kozlodoy_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.kozlodoy_button.clicked.connect(self.toggle_kozlodoy)
        layout.addWidget(self.kozlodoy_button)
        self.taxi_button = QPushButton("Запустить работу в Такси")
        self.taxi_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.taxi_button.clicked.connect(self.toggle_taxi)
        layout.addWidget(self.taxi_button)
        # self.fireman_button = QPushButton("Запустить работу Пожарным")
        # self.fireman_button.setStyleSheet("font-size: 16px; padding: 10px;")
        # self.fireman_button.clicked.connect(self.toggle_fireman)
        # layout.addWidget(self.fireman_button)
        self.chk_autorun = QCheckBox("Авто-Бег")
        self.chk_autorun.setStyleSheet("""
            QCheckBox::indicator { width: 15px; height: 15px; }
            QCheckBox::indicator:unchecked { background-color: #bdbdbd; border: 2px solid #757575; border-radius: 7px; }
            QCheckBox::indicator:checked { background-color: #ff7043; border: 2px solid #ffa726; border-radius: 7px; }
            QCheckBox { font-size: 16px; }
        """)
        self.chk_autorun.toggled.connect(self.toggle_autorun)
        layout.addWidget(self.chk_autorun)
        self.work_hint_label = QLabel("")
        self.work_hint_label.setStyleSheet("font-size: 16px; color: #ff7043;")
        layout.addWidget(self.work_hint_label)
        layout.addStretch()
        return widget

    def create_cook_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        title = QLabel("Крафты")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px;")
        layout.addWidget(title)
        cook_header = QLabel("Создание Блюд")
        cook_header.setAlignment(Qt.AlignCenter)
        cook_header.setStyleSheet("font-size: 20px; margin-top: 20px;")
        layout.addWidget(cook_header)
        cook_desc = QLabel("Запустите скрипт для выполнения специальной операции по созданию блюд.")
        cook_desc.setAlignment(Qt.AlignCenter)
        cook_desc.setWordWrap(True)
        cook_desc.setStyleSheet("font-size: 16px; color: #555555;")
        layout.addWidget(cook_desc)
        self.cook_error_label = QLabel("")
        self.cook_error_label.setStyleSheet("color: #ff7043; font-size: 16px;")
        layout.addWidget(self.cook_error_label)
        form_layout = QHBoxLayout()
        form_label = QLabel("Количество блюд:")
        form_label.setStyleSheet("font-size: 16px;")
        self.cook_input = QLineEdit()
        self.cook_input.setPlaceholderText("Введите число")
        self.cook_input.setStyleSheet("font-size: 16px; padding: 5px;")
        form_layout.addWidget(form_label)
        form_layout.addWidget(self.cook_input)
        layout.addLayout(form_layout)
        # Добавляем выбор блюда
        dish_layout = QHBoxLayout()
        dish_label = QLabel("Выберите блюдо:")
        dish_label.setStyleSheet("font-size: 16px;")
        self.dish_combo = QComboBox()
        self.dish_combo.addItems(["Салат", "Смузи", "Рагу"])  # Блюда из меню
        self.dish_combo.setStyleSheet("font-size: 16px; padding: 5px;")
        dish_layout.addWidget(dish_label)
        dish_layout.addWidget(self.dish_combo)
        layout.addLayout(dish_layout)
        # Удалить строку: self.processes = {}
        self.cookbot_running = False  # Оставляем инициализацию флага
        self.cook_button = QPushButton("Запустить")
        self.cook_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.cook_button.clicked.connect(self.toggle_cook)
        layout.addWidget(self.cook_button)
        kosyaki_header = QLabel("Создание Косяков")
        kosyaki_header.setAlignment(Qt.AlignCenter)
        kosyaki_header.setStyleSheet("font-size: 20px; margin-top: 20px;")
        layout.addWidget(kosyaki_header)
        kosyaki_desc = QLabel("Запустите скрипт для выполнения специальной операции по обработке косяков.")
        kosyaki_desc.setAlignment(Qt.AlignCenter)
        kosyaki_desc.setWordWrap(True)
        kosyaki_desc.setStyleSheet("font-size: 16px; color: #555555;")
        layout.addWidget(kosyaki_desc)
        self.kosyaki_button = QPushButton("Запустить Косюки")
        self.kosyaki_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.kosyaki_button.clicked.connect(self.toggle_kosyaki)
        layout.addWidget(self.kosyaki_button)
        layout.addStretch()
        return widget

    def create_automood_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        title = QLabel("Пассивные функции")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px;")
        layout.addWidget(title)
        automood_instr = QLabel("Настройте функцию Авто-Настроение.")
        automood_instr.setAlignment(Qt.AlignCenter)
        layout.addWidget(automood_instr)
        automood_label = QLabel("Клавиша Авто-Настроения:")
        automood_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(automood_label)
        self.automood_key_input = QLineEdit()
        self.automood_key_input.setPlaceholderText("Введите клавишу, например: L")
        self.automood_key_input.setStyleSheet("font-size: 16px; padding: 5px;")
        layout.addWidget(self.automood_key_input)
        self.automood_launch_button = QPushButton("Запустить Авто-Настроение")
        self.automood_launch_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.automood_launch_button.clicked.connect(self.toggle_automood)
        layout.addWidget(self.automood_launch_button)
        autorun_instr = QLabel("Настройте функцию Авто-Бег (эмуляция нажатия выбранной клавиши).")
        autorun_instr.setAlignment(Qt.AlignCenter)
        layout.addWidget(autorun_instr)
        autorun_label = QLabel("Клавиша Авто-Бег:")
        autorun_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(autorun_label)
        self.autorun_key_input = QLineEdit()
        self.autorun_key_input.setPlaceholderText("Введите клавишу, например: J")
        self.autorun_key_input.setStyleSheet("font-size: 16px; padding: 5px;")
        layout.addWidget(self.autorun_key_input)
        # self.autorun_launch_button = QPushButton("Запустить Авто-Бег")
        # self.autorun_launch_button.setStyleSheet("font-size: 16px; padding: 10px;")
        # self.autorun_launch_button.clicked.connect(self.toggle_autorun)
        # layout.addWidget(self.autorun_launch_button)
        autoeat_instr = QLabel("Настройте функцию Авто-Еда (эмуляция нажатия клавиши при недостатке еды).")
        autoeat_instr.setAlignment(Qt.AlignCenter)
        layout.addWidget(autoeat_instr)
        autoeat_label = QLabel("Клавиша Авто-Еда:")
        autoeat_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(autoeat_label)
        self.autoeat_key_input = QLineEdit()
        self.autoeat_key_input.setPlaceholderText("Введите клавишу, например: H")
        self.autoeat_key_input.setStyleSheet("font-size: 16px; padding: 5px;")
        layout.addWidget(self.autoeat_key_input)
        self.autoeat_launch_button = QPushButton("Запустить Авто-Еда")
        self.autoeat_launch_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.autoeat_launch_button.clicked.connect(self.toggle_autoeat)
        layout.addWidget(self.autoeat_launch_button)
        settings = load_settings()
        self.automood_key_input.setText(settings.get("automood_key", "l"))
        self.autorun_key_input.setText(settings.get("autorun_key", "+"))
        self.autoeat_key_input.setText(settings.get("autoeat_key", "o"))
        layout.addStretch()
        self.passive_save_button = QPushButton("Сохранить настройки")
        self.passive_save_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.passive_save_button.clicked.connect(self.save_passive_settings)
        layout.addWidget(self.passive_save_button)
        return widget

    def create_contracts_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        title = QLabel("Контракты")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px;")
        layout.addWidget(title)
        desc = QLabel("Запустите скрипты для выполнения контрактов.")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 16px;")
        layout.addWidget(desc)
        self.shveika_button = QPushButton("Запустить Швейную фабрику")
        self.shveika_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.shveika_button.clicked.connect(self.toggle_shveika)
        layout.addWidget(self.shveika_button)
        self.skolzkaya_button = QPushButton("Запустить Скользкая дорога")
        self.skolzkaya_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.skolzkaya_button.clicked.connect(self.toggle_skolzkaya)
        layout.addWidget(self.skolzkaya_button)
        self.schems_button = QPushButton("Запустить Схемы")
        self.schems_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.schems_button.clicked.connect(self.toggle_schems)
        layout.addWidget(self.schems_button)
        layout.addStretch()
        return widget

    def create_sportzal_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        title = QLabel("Спортзал")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px;")
        layout.addWidget(title)
        desc = QLabel("Запустите программу для тренировки мышц в спортзале.")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 16px;")
        layout.addWidget(desc)
        self.kachalka_launch_button = QPushButton("Запустить тренировку в спортзале")
        self.kachalka_launch_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.kachalka_launch_button.clicked.connect(self.toggle_kachalka)
        layout.addWidget(self.kachalka_launch_button)
        layout.addStretch()
        return widget

    def create_settings_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        title = QLabel("Настройки")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px;")
        layout.addWidget(title)
        # Поле для ввода пароля
        password_label = QLabel("Пароль:")
        password_label.setAlignment(Qt.AlignCenter)
        password_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(password_label)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("font-size: 16px; padding: 5px;")
        layout.addWidget(self.password_input)
        # Комбобокс для выбора персонажа (русские слова)
        character_label = QLabel("Персонаж:")
        character_label.setAlignment(Qt.AlignCenter)
        character_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(character_label)
        self.character_combo = QComboBox()
        self.character_combo.setStyleSheet("font-size: 16px; padding: 5px;")
        character_display = {"First": "Первый", "Second": "Второй", "Third": "Третий"}
        for key, value in character_display.items():
            self.character_combo.addItem(value, key)
        layout.addWidget(self.character_combo)
        # Комбобокс для выбора точки спауна (русские слова)
        spawn_label = QLabel("Точка спауна:")
        spawn_label.setAlignment(Qt.AlignCenter)
        spawn_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(spawn_label)
        self.spawn_combo = QComboBox()
        self.spawn_combo.setStyleSheet("font-size: 16px; padding: 5px;")
        spawn_display = {"Dom": "Дом", "Kvartira": "Квартира", "Spawn": "Спавн", "Lasttochka": "Последняя точка"}
        for key, value in spawn_display.items():
            self.spawn_combo.addItem(value, key)
        layout.addWidget(self.spawn_combo)
        # Поле для ввода пути до Rage MP (ярлыка)
        path_label = QLabel("Путь до Rage MP:")
        path_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(path_label)
        self.rage_mp_path_input = QLineEdit()
        self.rage_mp_path_input.setPlaceholderText("Например: C:\\Users\\user\\Desktop\\RAGE Multiplayer.lnk")
        self.rage_mp_path_input.setStyleSheet("font-size: 16px; padding: 5px;")
        layout.addWidget(self.rage_mp_path_input)
        # Загрузка существующих настроек
        settings = load_settings()
        self.password_input.setText(settings.get("password", ""))
        current_char = settings.get("character", "First")
        index = self.character_combo.findData(current_char)
        if index >= 0:
            self.character_combo.setCurrentIndex(index)
        current_spawn = settings.get("spawn", "Dom")
        index = self.spawn_combo.findData(current_spawn)
        if index >= 0:
            self.spawn_combo.setCurrentIndex(index)
        self.rage_mp_path_input.setText(settings.get("rage_mp_path", ""))
        self.settings_save_button = QPushButton("Сохранить настройки")
        self.settings_save_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.settings_save_button.clicked.connect(self.save_settings_page)
        layout.addWidget(self.settings_save_button)
        self.launch_game_button = QPushButton("Запустить игру")
        self.launch_game_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.launch_game_button.clicked.connect(self.toggle_launch_game)
        layout.addWidget(self.launch_game_button)
        layout.addStretch()
        return widget

    def create_tg_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        title = QLabel("Telegram")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px;")
        layout.addWidget(title)
        desc = QLabel("Введите токен вашего Telegram бота и Chat ID, затем сохраните настройки.")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 16px;")
        layout.addWidget(desc)
        token_label = QLabel("Telegram Bot Token:")
        token_label.setAlignment(Qt.AlignCenter)
        token_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(token_label)
        self.telegram_token_input = QLineEdit()
        self.telegram_token_input.setPlaceholderText("Введите токен")
        self.telegram_token_input.setStyleSheet("font-size: 16px; padding: 5px;")
        layout.addWidget(self.telegram_token_input)
        chat_id_label = QLabel("Telegram Chat ID:")
        chat_id_label.setAlignment(Qt.AlignCenter)
        chat_id_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(chat_id_label)
        self.telegram_chat_id_input = QLineEdit()
        self.telegram_chat_id_input.setPlaceholderText("Введите Chat ID")
        self.telegram_chat_id_input.setStyleSheet("font-size: 16px; padding: 5px;")
        layout.addWidget(self.telegram_chat_id_input)
        settings = load_settings()
        self.telegram_token_input.setText(settings.get("telegram_token", ""))
        self.telegram_chat_id_input.setText(settings.get("telegram_chat_id", ""))
        self.tg_save_button = QPushButton("Сохранить настройки")
        self.tg_save_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.tg_save_button.clicked.connect(self.save_tg_settings)
        layout.addWidget(self.tg_save_button)
        layout.addStretch()
        return widget

    def create_demorgan_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        # Блок Demorgan
        title = QLabel("Пошив Формы")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px;")
        layout.addWidget(title)
        desc = QLabel("Скрипт для автоматизации процесса в деморгане.")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 16px; color: #555555;")
        layout.addWidget(desc)
        self.demorgan_button = QPushButton("Запустить Пошив Формы")
        self.demorgan_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.demorgan_button.clicked.connect(self.toggle_demorgan)
        layout.addWidget(self.demorgan_button)
        # Блок Tochilka
        sep_label = QLabel(" ")
        layout.addWidget(sep_label)
        tochilka_title = QLabel("Токарка")
        tochilka_title.setAlignment(Qt.AlignCenter)
        tochilka_title.setStyleSheet("font-size: 20px; margin-top: 20px;")
        layout.addWidget(tochilka_title)
        tochilka_desc = QLabel("Скрипт для заточки предметов (пример описания).")
        tochilka_desc.setAlignment(Qt.AlignCenter)
        tochilka_desc.setWordWrap(True)
        tochilka_desc.setStyleSheet("font-size: 16px; color: #555555;")
        layout.addWidget(tochilka_desc)
        self.tochilka_button = QPushButton("Запустить Точилку")
        self.tochilka_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.tochilka_button.clicked.connect(self.toggle_tochilka)
        layout.addWidget(self.tochilka_button)
        layout.addStretch()
        return widget

    def save_tg_settings(self):
        token = self.telegram_token_input.text().strip()
        chat_id = self.telegram_chat_id_input.text().strip()
        if token and chat_id:
            settings = load_settings()
            settings["telegram_token"] = token
            settings["telegram_chat_id"] = chat_id
            save_settings(settings)
            QMessageBox.information(self, "Настройки сохранены",
                                    f"Telegram настройки сохранены:\nToken: {token}\nChat ID: {chat_id}")
        else:
            QMessageBox.critical(self, "Ошибка", "Введите корректные значения для токена и Chat ID")

    def save_passive_settings(self):
        automood_key = self.automood_key_input.text().strip()
        autorun_key = self.autorun_key_input.text().strip()
        autoeat_key = self.autoeat_key_input.text().strip()
        if automood_key and autorun_key and autoeat_key:
            settings = load_settings()
            settings["automood_key"] = automood_key
            settings["autorun_key"] = autorun_key
            settings["autoeat_key"] = autoeat_key
            save_settings(settings)
            self.work_hint_label.setText(
                f"Настройки сохранены: Automood = {automood_key}, Autorun = {autorun_key}, Autoeat = {autoeat_key}"
            )
        else:
            self.work_hint_label.setText("Ошибка: введите корректные клавиши")

    def manual_reconnect(self):
        """
        Метод для ручного реконнекта игры.
        Если процесс реконнекта уже запущен, завершает его.
        Затем запускает процесс реконнекта, вызывая скрипт reconect.py и передавая путь к settings.json.
        Возвращает True, если процесс успешно запущен, иначе – False.
        """
        # Если процесс реконнекта уже существует, завершаем его
        if self.processes.get("reconnect") is not None:
            try:
                proc = self.processes["reconnect"]
                proc.terminate()
                proc.wait()
                self.processes["reconnect"] = None
                print("Предыдущий процесс реконнекта остановлен.")
            except Exception as e:
                print("Ошибка при остановке предыдущего реконнекта:", e)
        try:
            # Формируем путь к settings.json (предполагается, что он находится в корне проекта)
            settings_path = os.path.join(PROJECT_ROOT, "settings.json")
            # Запускаем скрипт reconect.py (путь должен быть указан в переменной RECONNECT_PATH)
            proc = subprocess.Popen(
                [PYTHON_EXEC, RECONNECT_PATH, settings_path],
                cwd=os.path.dirname(RECONNECT_PATH)
            )
            self.processes["reconnect"] = proc
            print("Manual Reconnect запущен, PID:", proc.pid)
            return True
        except Exception as e:
            print("Ошибка при запуске Manual Reconnect:", e)
            return False

    def send_screenshot(self):
        """Создает и отправляет кастомный скриншот"""
        try:
            from modules.OtherService.screenshot import take_screenshot

            screenshot_path = take_screenshot()
            if not screenshot_path:
                return False

            if send_screenshot_to_telegram(screenshot_path):
                os.remove(screenshot_path)
                print("Custom screenshot sent and deleted")
                return True
            return False

        except Exception as e:
            print(f"Error in custom screenshot: {str(e)}")
            return False
    def toggle_fullreconnect(self, checked: bool):
        """Управляет полным реконнектом"""
        try:
            if checked:
                from modules.OtherService.fullreconect import run_fullreconnect_bot
                self.fullreconnect_thread = threading.Thread(
                    target=run_fullreconnect_bot,
                    daemon=True
                )
                self.fullreconnect_thread.start()
                print("Полный реконнект запущен в отдельном потоке")
            else:
                if self.processes["fullreconnect"]:
                    self.processes["fullreconnect"].terminate()
                    self.processes["fullreconnect"] = None
                    print("Полный реконнект остановлен")

        except Exception as e:
            print(f"Ошибка в toggle_fullreconnect: {str(e)}")
            traceback.print_exc()
    def toggle_kosyaki(self):
        if self.processes.get("kosyaki") is None:
            # Получаем путь к текущему интерпретатору Python
            python_executable = sys.executable
            # Получаем путь к текущему скрипту
            script_path = sys.argv[0]
            try:
                self.processes["kosyaki"] = subprocess.Popen(
                    [python_executable, script_path, "--service=kosyaki"],
                    creationflags=subprocess.CREATE_NO_WINDOW  # Без окна
                )
                self.kosyaki_button.setText("Остановить создание Косяков")
                self.kosyaki_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Скрипт kosyaki запущен, PID:", self.processes["kosyaki"].pid)
            except Exception as e:
                print("Ошибка при запуске kosyaki:", e)
        else:
            try:
                self.processes["kosyaki"].terminate()
                self.processes["kosyaki"].wait()
                self.processes["kosyaki"] = None
                self.kosyaki_button.setText("Запустить создание Косяков")
                self.kosyaki_button.setStyleSheet("font-size: 16px; padding: 10px;")
                print("Скрипт kosyaki остановлен.")
            except Exception as e:
                print("Ошибка при остановке kosyaki:", e)

    def toggle_automood(self):
        if self.processes["automood"] is None:
            # Получаем путь к текущему интерпретатору Python
            python_executable = sys.executable
            # Получаем путь к текущему скрипту
            script_path = sys.argv[0]
            try:
                self.processes["automood"] = subprocess.Popen(
                    [python_executable, script_path, "--service=automood"],

                )
                self.automood_launch_button.setText("Остановить Авто-Настроение")
                self.automood_launch_button.setStyleSheet(
                    "font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Automood запущен, PID:", self.processes["automood"].pid)
            except Exception as e:
                print("Ошибка при запуске Automood:", e)
        else:
            try:
                self.processes["automood"].terminate()
                self.processes["automood"].wait()
                self.processes["automood"] = None
                self.automood_launch_button.setText("Запустить Авто-Настроение")
                self.automood_launch_button.setStyleSheet("font-size: 16px; padding: 10px;")
                print("Automood остановлен.")
            except Exception as e:
                print("Ошибка при остановке Automood:", e)

    def toggle_autorun(self):
        if self.processes["autorun"] is None:
            # Получаем путь к текущему интерпретатору Python
            python_executable = sys.executable
            # Получаем путь к текущему скрипту
            script_path = sys.argv[0]
            try:
                self.processes["autorun"] = subprocess.Popen(
                    [python_executable, script_path, "--service=autorun"],
                    creationflags=subprocess.CREATE_NO_WINDOW  # Без окна
                )
                self.autorun_launch_button.setText("Остановить Авто-Бег")
                self.autorun_launch_button.setStyleSheet(
                    "font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                self.chk_autorun.setChecked(True)
                print("Autorun запущен, PID:", self.processes["autorun"].pid)
            except Exception as e:
                print("Ошибка при запуске Autorun:", e)
        else:
            try:
                self.processes["autorun"].terminate()
                self.processes["autorun"].wait()
                self.processes["autorun"] = None
                self.autorun_launch_button.setText("Запустить Авто-Бег")
                self.autorun_launch_button.setStyleSheet("font-size: 16px; padding: 10px;")
                self.chk_autorun.setChecked(False)
                print("Autorun остановлен.")
            except Exception as e:
                print("Ошибка при остановке Autorun:", e)

    def toggle_autoeat(self):
        if self.processes["autoeat"] is None:
            # Получаем путь к текущему интерпретатору Python
            python_executable = sys.executable
            # Получаем путь к текущему скрипту
            script_path = sys.argv[0]
            try:
                self.processes["autoeat"] = subprocess.Popen(
                    [python_executable, script_path, "--service=autoeat"],


                )
                self.autoeat_launch_button.setText("Остановить Авто-Еда")
                self.autoeat_launch_button.setStyleSheet(
                    "font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Autoeat запущен, PID:", self.processes["autoeat"].pid)
            except Exception as e:
                print("Ошибка при запуске Autoeat:", e)
        else:
            try:
                self.processes["autoeat"].terminate()
                self.processes["autoeat"].wait()
                self.processes["autoeat"] = None
                self.autoeat_launch_button.setText("Запустить Авто-Еда")
                self.autoeat_launch_button.setStyleSheet("font-size: 16px; padding: 10px;")
                print("Autoeat остановлен.")
            except Exception as e:
                print("Ошибка при остановке Autoeat:", e)

    def toggle_antiafk(self):
        if self.processes["antiafk"] is None:
            # Получаем путь к текущему интерпретатору Python
            python_executable = sys.executable
            # Получаем путь к текущему скрипту
            script_path = sys.argv[0]
            try:
                self.processes["antiafk"] = subprocess.Popen(
                    [python_executable, script_path, "--service=antiafk"],
                    creationflags=subprocess.CREATE_NO_WINDOW  # Без окна
                )
                self.antiafk_button.setText("Остановить antiafk")
                self.antiafk_button.setStyleSheet(
                    "font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("antiafk запущен, PID:", self.processes["antiafk"].pid)
            except Exception as e:
                print("Ошибка при запуске antiafk:", e)
        else:
            try:
                self.processes["antiafk"].terminate()
                self.processes["antiafk"].wait()
                self.processes["antiafk"] = None
                self.antiafk_button.setText("Запустить antiafk")
                self.antiafk_button.setStyleSheet("font-size: 16px; padding: 10px;")
                print("antiafk остановлен.")
            except Exception as e:
                print("Ошибка при остановке antiafk:", e)

    def toggle_koleso(self, checked):
        print(f"[DEBUG] Toggle koleso: {checked}")
        try:
            if checked:
                if self.processes["koleso"] is None:
                    command = [
                        sys.executable,
                        sys.argv[0],
                        "--service=koleso"
                    ]

                    # Запускаем процесс с перенаправлением вывода
                    self.processes["koleso"] = subprocess.Popen(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        encoding='utf-8',
                        bufsize=1,  # Строковая буферизация
                        cwd=os.path.dirname(os.path.abspath(__file__)),
                    )

                    # Создаем поток для чтения вывода
                    def output_reader(process, service_name):
                        while True:
                            output = process.stdout.readline()
                            if output == '' and process.poll() is not None:
                                break
                            if output:
                                print(f"[{service_name}] {output.strip()}")

                        # После завершения процесса
                        self.processes["koleso"] = None
                        self.chk_koleso.blockSignals(True)
                        self.chk_koleso.setChecked(False)
                        self.chk_koleso.blockSignals(False)

                    # Запускаем поток чтения вывода
                    threading.Thread(
                        target=output_reader,
                        args=(self.processes["koleso"], "koleso"),
                        daemon=True
                    ).start()

                    # Обновляем UI
                    self.chk_koleso.blockSignals(True)
                    self.chk_koleso.setChecked(True)
                    self.chk_koleso.blockSignals(False)

            else:
                if self.processes["koleso"] is not None:
                    # Завершаем процесс
                    self.processes["koleso"].terminate()
                    self.processes["koleso"] = None

                    # Обновляем UI
                    self.chk_koleso.blockSignals(True)
                    self.chk_koleso.setChecked(False)
                    self.chk_koleso.blockSignals(False)

        except Exception as e:
            print(f"[ERROR] Koleso error: {str(e)}")
            traceback.print_exc()
    def toggle_lottery(self, checked):
        print(f"[DEBUG] Toggle lottery: {checked}")
        if checked:
            if self.processes["lottery"] is None:
                try:
                    command = [sys.executable, sys.argv[0], "--service=lottery"]
                    self.processes["lottery"] = subprocess.Popen(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        encoding='utf-8'
                    )
                    self.chk_lottery.setChecked(True)  # Обновляем состояние чекбокса
                    threading.Thread(

                        args=(self.processes["lottery"], "lottery"),
                        daemon=True
                    ).start()
                except Exception as e:
                    print(f"[ERROR] Failed to start lottery: {str(e)}")
                    self.chk_lottery.setChecked(False)
        else:
            if self.processes["lottery"] is not None:
                try:
                    self.processes["lottery"].terminate()
                    self.processes["lottery"] = None
                    self.chk_lottery.setChecked(False)  # Обновляем состояние чекбокса
                except Exception as e:
                    print(f"[ERROR] Failed to stop lottery: {str(e)}")



    def toggle_cook(self):
        if self.processes["cook"] is None:
            dish = self.dish_combo.currentText()
            quantity = self.cook_input.text()

            if not quantity.isdigit():
                self.cook_error_label.setText("Введите число!")
                return

            try:
                script_path = os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__),
                        "modules/CraftService/cook.py"
                    )
                )

                self.processes["cook"] = subprocess.Popen(
                    [
                        sys.executable,
                        script_path,
                        "--service=cookbot",
                        "--dish", dish,
                        "--quantity", quantity
                    ],

                )

                # Стиль как в toggle_waxta
                self.cook_button.setText("Остановить приготовление")
                self.cook_button.setStyleSheet(
                    "font-size: 16px; padding: 10px; background-color: #ff7043; color: white;"
                )
                print("CookBot запущен, PID:", self.processes["cook"].pid)

            except Exception as e:
                print("Ошибка при запуске CookBot:", e)
                self.cook_error_label.setText(f"Ошибка: {str(e)}")

        else:
            try:
                self.processes["cook"].terminate()
                self.processes["cook"].wait()
                self.processes["cook"] = None

                # Возвращаем базовый стиль
                self.cook_button.setText("Запустить приготовление")
                self.cook_button.setStyleSheet("font-size: 16px; padding: 10px;")
                print("Приготовление остановлено")

            except Exception as e:
                print("Ошибка при остановке CookBot:", e)
                self.cook_error_label.setText(f"Ошибка остановки: {str(e)}")

    def toggle_waxta(self):
        if self.processes["waxta"] is None:
            # Получаем путь к текущему интерпретатору Python
            python_executable = sys.executable
            # Получаем путь к текущему скрипту
            script_path = sys.argv[0]
            try:
                self.processes["waxta"] = subprocess.Popen(
                    [python_executable, script_path, "--service=waxta"],
                    creationflags=subprocess.CREATE_NO_WINDOW  # Без окна
                )
                self.waxta_button.setText("Остановить работу на Шахте")
                self.waxta_button.setStyleSheet(
                    "font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Waxta запущена, PID:", self.processes["waxta"].pid)
            except Exception as e:
                print("Ошибка при запуске Шахты:", e)
        else:
            try:
                self.processes["waxta"].terminate()
                self.processes["waxta"].wait()
                self.processes["waxta"] = None
                self.waxta_button.setText("Запустить работу на Шахте")
                self.waxta_button.setStyleSheet("font-size: 16px; padding: 10px;")
                print("Шахта остановлена.")
            except Exception as e:
                print("Ошибка при остановке Шахты:", e)

    def toggle_port(self):
        if self.processes["port"] is None:
            # Получаем путь к текущему интерпретатору Python
            python_executable = sys.executable
            # Получаем путь к текущему скрипту
            script_path = sys.argv[0]
            try:
                self.processes["port"] = subprocess.Popen(
                    [python_executable, script_path, "--service=port"],
                      # Без окна
                )
                self.port_button.setText("Остановить работу в Порту")
                self.port_button.setStyleSheet(
                    "font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Порт запущена, PID:", self.processes["port"].pid)
            except Exception as e:
                print("Ошибка при запуске Порта:", e)
        else:
            try:
                self.processes["port"].terminate()
                self.processes["port"].wait()
                self.processes["port"] = None
                self.port_button.setText("Запустить работу в Порту")
                self.port_button.setStyleSheet("font-size: 16px; padding: 10px;")
                print("Порт остановлена.")
            except Exception as e:
                print("Ошибка при остановке работы в Порту", e)

    def toggle_stroyka(self):
        if self.processes["stroyka"] is None:
            # Получаем путь к текущему интерпретатору Python
            python_executable = sys.executable
            # Получаем путь к текущему скрипту
            script_path = sys.argv[0]
            try:
                try:

                    self.processes["stroyka"] = subprocess.Popen(
                        [python_executable, script_path, "--service=stroyka"],


                        text=True,
                        encoding='utf-8'
                    )
                    print(f"Запущен процесс с PID {self.processes['stroyka'].pid}, вывод перенаправлен в stroyka_log.txt")
                finally:print('Привет')
                self.stroyka_button.setText("Остановить работу на Стройке")
                self.stroyka_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Стройка запущена, PID:", self.processes["stroyka"].pid)
            except Exception as e:
                print("Ошибка при запуске Стройки:", e)
        else:
            try:
                self.processes["stroyka"].terminate()
                self.processes["stroyka"].wait()
                self.processes["stroyka"] = None
                self.stroyka_button.setText("Запустить работу на Стройке")
                self.stroyka_button.setStyleSheet("font-size: 16px; padding: 10px;")
                print("Стройка остановлена.")
            except Exception as e:
                print("Ошибка при остановке Стройки:", e)

    def toggle_kozlodoy(self):
        if self.processes["kozlodoy"] is None:
            # Получаем путь к текущему интерпретатору Python
            python_executable = sys.executable
            # Получаем путь к текущему скрипту
            script_path = sys.argv[0]
            try:
                self.processes["kozlodoy"] = subprocess.Popen(
                    [python_executable, script_path, "--service=kozlodoy"],

                )
                self.kozlodoy_button.setText("Остановить работу на Ферме")
                self.kozlodoy_button.setStyleSheet(
                    "font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Работа на Ферме запущена, PID:", self.processes["kozlodoy"].pid)
            except Exception as e:
                print("Ошибка при запуске работы на Ферме:", e)
        else:
            try:
                self.processes["kozlodoy"].terminate()
                self.processes["kozlodoy"].wait()
                self.processes["kozlodoy"] = None
                self.kozlodoy_button.setText("Запустить работу на Ферме")
                self.kozlodoy_button.setStyleSheet("font-size: 16px; padding: 10px;")
                print("Работа на Ферме остановлена.")
            except Exception as e:
                print("Ошибка при остановке работы на Ферме:", e)

    def toggle_taxi(self):
        if self.processes["taxi"] is None:

            try:
                if getattr(sys, 'frozen', False):
                    command = [sys.executable, "--service=taxi"]
                else:
                    command = [sys.executable, sys.argv[0], "--service=taxi"]

                self.processes["taxi"] = subprocess.Popen(
                    command,
                    stdout=open('taxi_log.txt', 'w'),  # Запись логов в файл
                    stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                self.taxi_button.setText("Остановить работу в такси")
                self.taxi_button.setStyleSheet(
                    "font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Работа в такси запущена, PID:", self.processes["taxi"].pid)
            except Exception as e:
                print("Ошибка при запуске работы в Такси:", e)
        else:
            try:
                self.processes["taxi"].terminate()
                self.processes["taxi"].wait()
                self.processes["taxi"] = None
                self.taxi_button.setText("Запустить работу в Такси")
                self.taxi_button.setStyleSheet("font-size: 16px; padding: 10px;")
                print("Работа в Такси остановлена.")
            except Exception as e:
                print("Ошибка при остановке работы в Такси:", e)
    # def toggle_fireman(self):
    #     if self.processes.get("fireman") is None:
    #         wd = os.path.dirname(FIREMAN_PATH)
    #         try:
    #             proc = subprocess.Popen([PYTHON_EXEC, FIREMAN_PATH], cwd=wd)
    #             self.processes["fireman"] = proc
    #             self.fireman_button.setText("Остановить работу Пожарным")
    #             self.fireman_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
    #             print("Fireman запущен, PID:", proc.pid)
    #         except Exception as e:
    #             print("Ошибка при запуске Fireman:", e)
    #     else:
    #         try:
    #             self.processes["fireman"].terminate()
    #             self.processes["fireman"].wait()
    #             self.processes["fireman"] = None
    #             self.fireman_button.setText("Запустить работу Пожарным")
    #             self.fireman_button.setStyleSheet("font-size: 16px; padding: 10px;")
    #             print("Fireman остановлен.")
    #         except Exception as e:
    #             print("Ошибка при остановке Fireman:", e)

    def toggle_kachalka(self):
        if self.processes.get("kachalka") is None:
            # Получаем путь к текущему интерпретатору Python
            python_executable = sys.executable
            # Получаем путь к текущему скрипту
            script_path = sys.argv[0]
            try:
                self.processes["kachalka"] = subprocess.Popen(
                    [python_executable, script_path, "--service=kachalka"],
                    creationflags=subprocess.CREATE_NO_WINDOW  # Без окна
                )
                self.processes["kachalka"]
                self.kachalka_launch_button.setText("Остановить Спортзал")
                self.kachalka_launch_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Спортзал запущен (kachalka), PID:", self.processes["kachalka"].pid)
            except Exception as e:
                print("Ошибка при запуске Спортзала (kachalka):", e)
        else:
            try:
                self.processes["kachalka"].terminate()
                self.processes["kachalka"].wait()
                self.processes["kachalka"] = None
                self.kachalka_launch_button.setText("Запустить Спортзал")
                self.kachalka_launch_button.setStyleSheet("font-size: 16px; padding: 10px;")
                print("Спортзал остановлен.")
            except Exception as e:
                print("Ошибка при остановке Спортзала (kachalka):", e)

    def toggle_shveika(self):
        if self.processes.get("shveika") is None:
            python_executable = sys.executable
            script_path = sys.argv[0]

            print(f"[DEBUG] Путь к интерпретатору: {python_executable}")
            print(f"[DEBUG] Путь к скрипту: {script_path}")
            print(f"[DEBUG] Аргументы запуска: {[python_executable, script_path, '--service=shveika']}")

            try:
                self.processes["shveika"] = subprocess.Popen(
                    [python_executable, script_path, "--service=shveika"],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                self.shveika_button.setText("Остановить пошив Одежды")
                self.shveika_button.setStyleSheet(
                    "font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Shveika запущен, PID:", self.processes["shveika"].pid)
            except Exception as e:
                print("Ошибка при запуске Shveika:", e)
        else:
            try:
                self.processes["shveika"].terminate()
                self.processes["shveika"].wait()
                self.processes["shveika"] = None
                self.shveika_button.setText("Запустить пошив Одежды")
                self.shveika_button.setStyleSheet("font-size: 16px; padding: 10px;")
                print("Shveika остановлен.")
            except Exception as e:
                print("Ошибка при остановке Shveika:", e)

    def toggle_skolzkaya(self):
        if self.processes.get("skolzkaya") is None:
            python_executable = sys.executable
            script_path = sys.argv[0]
            try:
                self.processes["skolzkaya"] = subprocess.Popen(
                    [python_executable, script_path, "--service=skolzkaya"],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                self.skolzkaya_button.setText("Остановить Скользкая дорога")
                self.skolzkaya_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Skolzkaya запущен, PID:", self.processes["skolzkaya"].pid)
            except Exception as e:
                print("Ошибка при запуске Skolzkaya:", e)
        else:
            try:
                self.processes["skolzkaya"].terminate()
                self.processes["skolzkaya"].wait()
                self.processes["skolzkaya"] = None
                self.skolzkaya_button.setText("Запустить Скользкая дорога")
                self.skolzkaya_button.setStyleSheet("font-size: 16px; padding: 10px;")
                print("Skolzkaya остановлен.")
            except Exception as e:
                print("Ошибка при остановке Skolzkaya:", e)

    def toggle_schems(self):
        if self.processes.get("schems") is None:
            # Получаем путь к текущему интерпретатору Python
            python_executable = sys.executable
            # Получаем путь к текущему скрипту
            script_path = sys.argv[0]
            try:
                self.processes["schems"] = subprocess.Popen(
                    [python_executable, script_path, "--service=schems"],
                    creationflags=subprocess.CREATE_NO_WINDOW  # Без окна
                )
                self.schems_button.setText("Остановить Схемы")
                self.schems_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("schems запущен, PID:", self.processes["schems"].pid)
            except Exception as e:
                print("Ошибка при запуске schems:", e)
        else:
            try:
                self.processes["schems"].terminate()
                self.processes["schems"].wait()
                self.processes["schems"] = None
                self.schems_button.setText("Запустить Схемы")
                self.schems_button.setStyleSheet("font-size: 16px; padding: 10px;")
                print("schems остановлен.")
            except Exception as e:
                print("Ошибка при остановке schems:", e)

    def toggle_reconnect(self, checked: bool):
        """Управляет реконнектом через аргумент checked"""
        try:
            if checked:
                if self.processes.get("reconnect") is not None:
                    print("[DEBUG] Реконнект уже запущен")
                    return

                print("[DEBUG] Запуск реконнекта...")
                settings_path = os.path.join(PROJECT_ROOT, "settings.json")

                # Явно указываем полный путь к скрипту
                reconnect_script = os.path.abspath(
                    os.path.join(MODULES_BASE, "OtherService", "reconect.py")
                )

                proc = subprocess.Popen(
                    [
                        PYTHON_EXEC,
                        reconnect_script,
                        "--service=reconnect",
                        settings_path
                    ],

                    stderr=subprocess.STDOUT,

                )
                self.processes["reconnect"] = proc
                print(f"[DEBUG] PID процесса: {proc.pid}")
                time.sleep(2)  # Даем процессу время инициализироваться

                # Проверяем жизнеспособность процесса
                if proc.poll() is not None:
                    print("[ERROR] Процесс завершился сразу после запуска")
                    with open('reconnect.log', 'r') as f:
                        print(f"Логи процесса:\n{f.read()}")

                self.chk_myservice.setChecked(True)
            else:
                    # Остановка реконнекта
                    if self.processes.get("reconnect") is not None:
                        self.processes["reconnect"].terminate()
                    self.processes["reconnect"] = None
                    print("Реконнект остановлен")
                    self.chk_myservice.setChecked(False)  # Синхронизируем чекбокс
        except Exception as e:
            print(f"[CRITICAL] Ошибка: {str(e)}")
            traceback.print_exc()


    def check_game_active(self):
        if process_checker.is_game_active():
            self.inactive_counter = 0
            self.bots_killed_due_to_inactivity = False
        else:
            self.inactive_counter += 1
            if self.inactive_counter >= 180 and not self.bots_killed_due_to_inactivity:
                print("Игра не активна 3 минуты. Останавливаем всех ботов.")
                self.kill_all_bots()
                self.bots_killed_due_to_inactivity = True

    def save_settings_page(self):
        rage_mp_path = self.rage_mp_path_input.text().strip()
        if rage_mp_path:
            settings = load_settings()
            settings["password"] = self.password_input.text().strip()
            settings["character"] = self.character_combo.currentData()
            settings["spawn"] = self.spawn_combo.currentData()
            settings["rage_mp_path"] = rage_mp_path
            save_settings(settings)
            self.work_hint_label.setText(f"Настройки сохранены: Rage MP = {rage_mp_path}")
        else:
            self.work_hint_label.setText("Ошибка: введите корректный путь до Rage MP")

    def toggle_launch_game(self):
        # Проверка активности игры с помощью process_checker
        if process_checker.is_game_active():
            QMessageBox.information(self, "Информация", "Игра уже запущена!")
            return
        shortcut_path = self.rage_mp_path_input.text().strip()
        if not shortcut_path:
            QMessageBox.critical(self, "Ошибка", "Пожалуйста, введите путь до ярлыка Rage MP!")
            return
        if not os.path.exists(shortcut_path) or not shortcut_path.lower().endswith(".lnk"):
            QMessageBox.critical(self, "Ошибка", "Неверный путь или расширение файла! Укажите ярлык (.lnk).")
            return
        try:
            os.startfile(shortcut_path, "runas")
            print("Игра запущена через ярлык.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка запуска", f"Не удалось запустить игру: {e}")

    def toggle_demorgan(self):
        if self.processes["demorgan"] is None:
            # Получаем путь к текущему интерпретатору Python
            python_executable = sys.executable
            # Получаем путь к текущему скрипту
            script_path = sys.argv[0]
            try:
                self.processes["demorgan"] = subprocess.Popen(
                    [python_executable, script_path, "--service=demorgan"],
                    creationflags=subprocess.CREATE_NO_WINDOW  # Без окна
                )
                self.demorgan_button.setText("Остановить Пошив формы")
                self.demorgan_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Пошив формы запущен, PID:", self.processes["demorgan"].pid)
            except Exception as e:
                print("Ошибка при запуске Пошив формы:", e)
        else:
            try:
                self.processes["demorgan"].terminate()
                self.processes["demorgan"].wait()
                self.processes["demorgan"] = None
                self.demorgan_button.setText("Запустить Пошив формы")
                self.demorgan_button.setStyleSheet("font-size: 16px; padding: 10px;")
                print("Пошив формы остановлен.")
            except Exception as e:
                print("Ошибка при остановке Пошив формы:", e)

    def toggle_tochilka(self):
        if self.processes["tochilka"] is None:
            # Получаем путь к текущему интерпретатору Python
            python_executable = sys.executable
            # Получаем путь к текущему скрипту
            script_path = sys.argv[0]
            try:
                self.processes["tochilka"] = subprocess.Popen(
                    [python_executable, script_path, "--service=tochilka"],
                    creationflags=subprocess.CREATE_NO_WINDOW  # Без окна
                )
                self.tochilka_button.setText("Остановить Токарку")
                self.tochilka_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Точилка запущена, PID:", self.processes["tochilka"].pid)
            except Exception as e:
                print("Ошибка при запуске Точилки:", e)
        else:
            try:
                self.processes["tochilka"].terminate()
                self.processes["tochilka"].wait()
                self.processes["tochilka"] = None
                self.tochilka_button.setText("Запустить Токарку")
                self.tochilka_button.setStyleSheet("font-size: 16px; padding: 10px;")
                print("Точилка остановлена.")
            except Exception as e:
                print("Ошибка при остановке Точилки:", e)

    def periodic_license_check(self):
        if self.license_expiry:
            now = datetime.datetime.now()
            if now >= self.license_expiry:
                print(" Лицензия истекла. Завершение работы приложения.")
                error_dialog = QDialog(self)
                error_dialog.setWindowTitle("Ошибка лицензии")
                dlg_layout = QVBoxLayout(error_dialog)
                msg_label = QLabel("Срок действия лицензии истек. Приложение будет закрыто.")
                msg_label.setAlignment(Qt.AlignCenter)
                dlg_layout.addWidget(msg_label)
                error_dialog.exec()
                QApplication.quit()

    def update_license_label(self):
        if self.license_expiry:
            now = datetime.datetime.now()
            remaining = self.license_expiry - now
            if remaining.total_seconds() <= 0:
                self.license_label.setText("Подписка истекла")
            else:
                self.license_label.setText("Подписка до: " + self.license_expiry.strftime("%Y-%m-%d %H:%M"))
        else:
            self.license_label.setText("Лицензия не активирована")

    def check_keyboard_layout(self):
        if get_keyboard_layout() != LANG_ENGLISH:
            msgBox = QMessageBox(self)
            msgBox.setWindowFlags(msgBox.windowFlags() | Qt.WindowStaysOnTopHint)
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setWindowTitle("Внимание!")
            msgBox.setText("Пожалуйста, переключите раскладку клавиатуры на английскую, наш бот работает только с ней!")
            msgBox.exec()

    from pathlib import Path
    from modules.OtherService.screenshotstats import take_screenshot

    def send_stats(self):
        from modules.OtherService.screenshotstats import take_screenshot
        """
        Метод для создания и отправки скриншота статистики
        """
        try:
            # Создаем скриншот используя встроенный метод
            screenshot_path = take_screenshot()

            # Отправляем скриншот
            if send_screenshot_to_telegram(screenshot_path):
                os.remove(screenshot_path)
                print("Скриншот отправлен и удалён.")
                return True
            return False
        except Exception as e:
            print(f"Ошибка при создании скриншота: {str(e)}")
            return False


    def kill_all_bots(self):
        for key in self.processes:
            proc = self.processes[key]
            if proc is not None:
                try:
                    proc.terminate()
                    proc.wait()
                    print(f"{key} остановлен.")
                except Exception as e:
                    print(f"Ошибка при остановке {key}: {e}")
                self.processes[key] = None
        self.antiafk_button.setText("Запустить Anti-AFK")
        self.antiafk_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.cook_button.setText("Запустить")
        self.cook_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.waxta_button.setText("Запустить работу на Шахте")
        self.waxta_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.port_button.setText("Запустить работу в Порту")
        self.port_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.stroyka_button.setText("Запустить работу на Стройке")
        self.stroyka_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.kozlodoy_button.setText("Запустить работу на Ферме")
        self.kozlodoy_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.chk_koleso.setChecked(False)
        self.chk_lottery.setChecked(False)
        if hasattr(self, 'chk_autorun'):
            self.chk_autorun.setChecked(False)
        self.work_hint_label.setText("")

def run_telegram_bot():
    s = load_settings()
    token = s.get("telegram_token", "")
    if not token:
        print(">>> Нет 'telegram_token' в settings.json, бот не запустится.")
        return
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    def cmd_start(update: Update, context: CallbackContext):
        # Кнопки БЕЗ пробелов в начале
        keyboard = [
            [KeyboardButton("Anti-AFK"), KeyboardButton("Авто-колесо"), KeyboardButton("Лотерея")],
            [KeyboardButton("Реконнект"), KeyboardButton("Полный реконнект"),KeyboardButton("Скриншот"), KeyboardButton("Статистика")],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text("Выберите действие:", reply_markup=reply_markup)
        text = (
            "<b>Привет!</b> Я бот управления сервисами.\n"
            "Выберите действие, нажав кнопку внизу.\n\n"
            "<i>Список команд:</i>\n"
            "• Anti-AFK — запустить/остановить систему анти-АФК\n"
            "• Авто-колесо — провернуть колесо удачи\n"
            "• Лотерея — запустить/остановить лотерею\n"
            "• Реконнект — реконнект после рестарта\n"
            "• Полный реконнект — реконнект при вылете игры\n"
            "• Скриншот — скриншот в реальном времени\n"
            "• Статистика — сделать скриншот статистики и отправить его в Telegram\n"
        )


    dp.add_handler(CommandHandler("start", cmd_start))

    def msg_handler(update: Update, context: CallbackContext):
        text = update.message.text
        print(f"Получено сообщение: '{text}'")  # Отладка

        if text == "Anti-AFK":
            window.toggle_antiafk()
            status = "запущен" if window.processes["antiafk"] else "остановлен"
            update.message.reply_text(f"Anti-AFK: {status}")

        elif text == "Скриншот":
            if window.send_screenshot():
                update.message.reply_text("Скриншот в реальном времени отправлен!")
            else:
                update.message.reply_text("Ошибка при создании скриншота")


        elif text == "Авто-колесо":

            current_state = window.chk_koleso.isChecked()

            window.toggle_koleso(not current_state)

            new_state = window.chk_koleso.isChecked()  # Получаем актуальное состояние

            status = "запущено" if new_state else "остановлено"

            update.message.reply_text(f"Авто-колесо: {status}")


        elif text == "Лотерея":

            current_state = window.chk_lottery.isChecked()

            window.toggle_lottery(not current_state)

            new_state = window.chk_lottery.isChecked()

            status = "запущена" if new_state else "остановлена"

            update.message.reply_text(f"Лотерея: {status}")

        elif text == "Реконнект":
            current_state = window.processes.get("reconnect") is not None
            print(f"Текущее состояние: {current_state}")

            window.toggle_reconnect(checked=not current_state)
            time.sleep(1)  # Ожидаем обновления статуса

            new_state = window.processes.get("reconnect") is not None
            status = "запущен" if new_state else "остановлен"
            update.message.reply_text(f"Реконнект {status}")
        elif text == "Полный реконнект":
            is_active = window.processes.get("fullreconnect") is not None
            window.toggle_fullreconnect(checked=not is_active)
            status = "запущен" if not is_active else "остановлен"
            update.message.reply_text(f"Полный реконнект {status}")

        elif text == "Статистика":
            window.send_stats()
            update.message.reply_text("Статистика отправлена!")

        else:
            update.message.reply_text("Неизвестная команда")

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, msg_handler))
    updater.start_polling()

if __name__ == "__main__":

    app = QApplication(sys.argv)
    expiry_date = authenticate()

    window = MainWindow()
    window.setWindowTitle("Менеджер сервисов бота")
    window.setGeometry(100, 100, 900, 600)
    window.show()
    tg_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    tg_thread.start()
    print(">>> Telegram-бот запущен (используйте /start)")
    sys.exit(app.exec())
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(file))))