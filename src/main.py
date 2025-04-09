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





PYTHON_EXEC = sys.executable

def run_service_mode():
    print("Запуск сервисного режима!")
    for arg in sys.argv[1:]:
        print("Аргумент:", arg)
        if arg.startswith("--service="):
            service_name = arg.split("=")[1]
            print("Сервис:", service_name)
            if service_name == "antiafk":
                from modules.AntiAfkService.antiafk import run_background
                run_background()
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

                run_stroyka()
                sys.exit(0)
            elif service_name == "kozlodoy":
                from modules.WorkService.kozlodoy import run_kozlodoy

                run_kozlodoy()
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
                # Задаем параметры для командной строки
                sys.argv = ['main.py', '--service=cookbot', '--dish', 'Салат', '--quantity', '40']
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



SERVER_URL = "http://83.220.165.162:5000"
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

PYTHON_EXEC = sys.executable

# def get_device_id():
#     return hex(uuid.getnode())
#
# def get_hwid():
#     mac = str(uuid.getnode())
#     computer_name = os.environ.get('COMPUTERNAME', 'unknown')
#     processor = platform.processor()
#     combined = mac + computer_name + processor
#     return hashlib.sha256(combined.encode()).hexdigest()

# def validate_key(key: str):
#     hwid = get_hwid()
#     print(f" Отправляем на сервер:\n  Ключ: {key}\n  HWID: {hwid}")
#     try:
#         response = requests.post(f"{SERVER_URL}/validate", json={"key": key, "hwid": hwid})
#         data = response.json()
#         print(f" Ответ сервера: {data}")
#         if response.status_code == 200:
#             expiry_date_str = data.get("expiry_date")
#             expiry_date = datetime.datetime.strptime(expiry_date_str, "%Y-%m-%d %H:%M:%S")
#             print(f" Ключ действителен. Подписка до {expiry_date}")
#             return True, expiry_date
#         else:
#             print(f"❌ Ошибка: {data.get('message', 'Unknown error')}")
#             return False, None
#     except requests.RequestException as e:
#         print(f" Ошибка подключения к серверу: {e}")
#         return False, None

# def load_license():
#     if os.path.exists(LICENSE_FILE):
#         try:
#             with open(LICENSE_FILE, "r") as f:
#                 license_info = json.load(f)
#             stored_hwid = license_info.get("hwid")
#             current_hwid = get_hwid()
#             if stored_hwid != current_hwid:
#                 print(" HWID не совпадает! Требуется повторная активация.")
#                 return None
#             expiry_date_str = license_info.get("expiry_date")
#             if expiry_date_str:
#                 return datetime.datetime.strptime(expiry_date_str, "%Y-%m-%d %H:%M:%S")
#         except Exception as e:
#             print(f" Ошибка загрузки лицензии: {e}")
#     return None

# def save_license(key, expiry_date):
#     license_info = {
#         "key": key,
#         "hwid": get_hwid(),
#         "expiry_date": expiry_date.strftime("%Y-%m-%d %H:%M:%S")
#     }
#     try:
#         with open(LICENSE_FILE, "w") as f:
#             json.dump(license_info, f)
#         print(f"Лицензия сохранена: подписка до {expiry_date}")
#     except Exception as e:
#         print(f" Ошибка при сохранении лицензии: {e}")

def send_screenshot_to_telegram(screenshot_path):
    """
    Загружает настройки из settings.json, отправляет скриншот в Telegram (через sendPhoto)
    и возвращает True, если отправка успешна.
    """
    # Определяем корневую папку проекта
    settings_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "settings.json"))
    print(f"Using settings path: {settings_path}")
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки настроек из {settings_path}: {e}")
        return False

    token = settings.get("telegram_token", "")
    chat_id = settings.get("telegram_chat_id", "")
    if not token or not chat_id:
        print("telegram_token или telegram_chat_id не заданы в настройках.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    try:
        with open(screenshot_path, "rb") as photo:
            response = requests.post(url, data={"chat_id": chat_id}, files={"photo": photo})
        if response.status_code == 200:
            print("Скриншот успешно отправлен в Telegram.")
            return True
        else:
            print(f"Ошибка отправки скриншота: {response.text}")
            return False
    except Exception as e:
        print(f"Исключение при отправке скриншота: {e}")
        return False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Менеджер сервисов бота")
        self.setGeometry(100, 100, 900, 600)
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
            "demorgan": None,
            "tochilka": None
        }

        self.inactive_counter = 0
        self.bots_killed_due_to_inactivity = False

        # self.license_expiry = load_license()
        #
        # self.license_check_timer = QTimer(self)
        # self.license_check_timer.timeout.connect(self.periodic_license_check)
        # self.license_check_timer.start(3600000)

        # self.keyboard_timer = QTimer(self)
        # self.keyboard_timer.timeout.connect(self.check_keyboard_layout)
        # self.keyboard_timer.start(10000)

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

        # self.license_label = QLabel()
        # self.license_label.setStyleSheet("font-size: 14px; color: #ff7043;")
        # left_layout.addWidget(self.license_label)
        # left_layout.setAlignment(self.license_label, Qt.AlignBottom)

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

        # self.license_timer = QTimer(self)
        # self.license_timer.timeout.connect(self.update_license_label)
        # self.license_timer.start(1000)

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
        self.fireman_button = QPushButton("Запустить работу Пожарным")
        self.fireman_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.fireman_button.clicked.connect(self.toggle_fireman)
        layout.addWidget(self.fireman_button)
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
        self.autorun_launch_button = QPushButton("Запустить Авто-Бег")
        self.autorun_launch_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.autorun_launch_button.clicked.connect(self.toggle_autorun)
        layout.addWidget(self.autorun_launch_button)
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
                    creationflags=subprocess.CREATE_NO_WINDOW  # Без окна
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
                    creationflags=subprocess.CREATE_NO_WINDOW  # Без окна
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
            self.processes["antiafk"] = subprocess.Popen([PYTHON_EXEC, ANTIAFK_PATH], cwd=PROJECT_ROOT)
            self.antiafk_button.setText("Остановить Anti-AFK")
            self.antiafk_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
        else:
            self.processes["antiafk"].terminate()
            self.processes["antiafk"].wait()
            self.processes["antiafk"] = None
            self.antiafk_button.setText("Запустить Anti-AFK")
            self.antiafk_button.setStyleSheet("font-size: 16px; padding: 10px;")

    def toggle_koleso(self, checked):
        if checked:
            wd = os.path.dirname(KRUTKAKOLES_PATH)
            try:
                proc = subprocess.Popen([PYTHON_EXEC, KRUTKAKOLES_PATH], cwd=wd)
                self.processes["koleso"] = proc
                print("Крутка колеса запущена, PID:", proc.pid)
            except Exception as e:
                print("Ошибка при запуске Крутки колеса:", e)
        else:
            if self.processes.get("koleso") is not None:
                try:
                    self.processes["koleso"].terminate()
                    self.processes["koleso"].wait()
                    print("Крутка колеса остановлена.")
                except Exception as e:
                    print("Ошибка при остановке Крутки колеса:", e)
                self.processes["koleso"] = None

    def toggle_lottery(self, checked):
        if checked:
            wd = os.path.dirname(LOTTERY_PATH)
            try:
                proc = subprocess.Popen([PYTHON_EXEC, LOTTERY_PATH], cwd=wd)
                self.processes["lottery"] = proc
                print("Лотерея запущена, PID:", proc.pid)
            except Exception as e:
                print("Ошибка при запуске Лотереи:", e)
        else:
            if self.processes.get("lottery") is not None:
                try:
                    self.processes["lottery"].terminate()
                    self.processes["lottery"].wait()
                    print("Лотерея остановлена.")
                except Exception as e:
                    print("Ошибка при остановке Лотереи:", e)
                self.processes["lottery"] = None

    def toggle_cook(self):
        if self.cookbot_running:
            print("Остановка CookBot")
            self.cookbot_process.terminate()  # Завершаем процесс CookBot
            self.cookbot_process = None  # Очищаем процесс
            self.cookbot_running = False  # Устанавливаем флаг в False
            self.cook_button.setText("Запустить")  # Меняем текст кнопки
        else:
            print("Запуск CookBot...")

            # Получаем параметры блюда и количества порций из интерфейса
            dish = self.dish_combo.currentText()  # Выбираем блюдо из комбобокса
            quantity = self.cook_input.text()  # Получаем количество порций

            # Проверяем, что количество порций введено корректно
            if not quantity.isdigit():
                self.cook_error_label.setText("Пожалуйста, введите корректное количество порций.")
                return

            # Преобразуем количество порций в число (если необходимо)
            quantity = int(quantity)

            # Задаем параметры командной строки, используя значения из интерфейса
            sys.argv = ['main.py', '--service=cookbot', '--dish', dish, '--quantity', str(quantity)]

            # Импортируем и запускаем функцию из cook.py
            from modules.CraftService.cook import run_cookbot
            run_cookbot()

            self.cookbot_running = True  # Устанавливаем флаг в True
            self.cook_button.setText("Остановить")  # Меняем текст кнопки на "Остановить"

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
                    creationflags=subprocess.CREATE_NO_WINDOW  # Без окна
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
                self.processes["stroyka"] = subprocess.Popen(
                    [python_executable, script_path, "--service=stroyka"],
                    creationflags=subprocess.CREATE_NO_WINDOW  # Без окна
                )
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
                    creationflags=subprocess.CREATE_NO_WINDOW  # Без окна
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
    def toggle_fireman(self):
        if self.processes.get("fireman") is None:
            wd = os.path.dirname(FIREMAN_PATH)
            try:
                proc = subprocess.Popen([PYTHON_EXEC, FIREMAN_PATH], cwd=wd)
                self.processes["fireman"] = proc
                self.fireman_button.setText("Остановить работу Пожарным")
                self.fireman_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Fireman запущен, PID:", proc.pid)
            except Exception as e:
                print("Ошибка при запуске Fireman:", e)
        else:
            try:
                self.processes["fireman"].terminate()
                self.processes["fireman"].wait()
                self.processes["fireman"] = None
                self.fireman_button.setText("Запустить работу Пожарным")
                self.fireman_button.setStyleSheet("font-size: 16px; padding: 10px;")
                print("Fireman остановлен.")
            except Exception as e:
                print("Ошибка при остановке Fireman:", e)

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
            wd = os.path.dirname(SKOLZKAYA_PATH)
            try:
                proc = subprocess.Popen([PYTHON_EXEC, SKOLZKAYA_PATH], cwd=wd)
                self.processes["skolzkaya"] = proc
                self.skolzkaya_button.setText("Остановить Скользкая дорога")
                self.skolzkaya_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Skolzkaya запущен, PID:", proc.pid)
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

    def toggle_reconnect(self, checked):
        if checked:
            try:
                settings_path = os.path.join(PROJECT_ROOT, "settings.json")
                proc = subprocess.Popen([PYTHON_EXEC, RECONNECT_PATH, settings_path],
                                        cwd=os.path.dirname(RECONNECT_PATH))
                self.processes["reconnect"] = proc
                print("Reconnect запущен, PID:", proc.pid)
            except Exception as e:
                print("Ошибка запуска reconnect:", e)
        else:
            if self.processes.get("reconnect") is not None:
                try:
                    proc = self.processes["reconnect"]
                    proc.terminate()
                    proc.wait()
                    self.processes["reconnect"] = None
                    print("Reconnect остановлен.")
                except Exception as e:
                    print("Ошибка при остановке reconnect:", e)

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
            wd = os.path.dirname(DEMORGAN_PATH)
            try:
                proc = subprocess.Popen([PYTHON_EXEC, DEMORGAN_PATH], cwd=wd)
                self.processes["demorgan"] = proc
                self.demorgan_button.setText("Остановить Пошив формы")
                self.demorgan_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Пошив формы запущен, PID:", proc.pid)
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
            wd = os.path.dirname(TOCHILKA_PATH)
            try:
                proc = subprocess.Popen([PYTHON_EXEC, TOCHILKA_PATH], cwd=wd)
                self.processes["tochilka"] = proc
                self.tochilka_button.setText("Остановить Токарку")
                self.tochilka_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Точилка запущена, PID:", proc.pid)
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

    # def periodic_license_check(self):
    #     if self.license_expiry:
    #         now = datetime.datetime.now()
    #         if now >= self.license_expiry:
    #             print(" Лицензия истекла. Завершение работы приложения.")
    #             error_dialog = QDialog(self)
    #             error_dialog.setWindowTitle("Ошибка лицензии")
    #             dlg_layout = QVBoxLayout(error_dialog)
    #             msg_label = QLabel("Срок действия лицензии истек. Приложение будет закрыто.")
    #             msg_label.setAlignment(Qt.AlignCenter)
    #             dlg_layout.addWidget(msg_label)
    #             error_dialog.exec()
    #             QApplication.quit()
    #
    # def update_license_label(self):
    #     if self.license_expiry:
    #         now = datetime.datetime.now()
    #         remaining = self.license_expiry - now
    #         if remaining.total_seconds() <= 0:
    #             self.license_label.setText("Подписка истекла")
    #         else:
    #             self.license_label.setText("Подписка до: " + self.license_expiry.strftime("%Y-%m-%d %H:%M"))
    #     else:
    #         self.license_label.setText("Лицензия не активирована")

    def check_keyboard_layout(self):
        if get_keyboard_layout() != LANG_ENGLISH:
            msgBox = QMessageBox(self)
            msgBox.setWindowFlags(msgBox.windowFlags() | Qt.WindowStaysOnTopHint)
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setWindowTitle("Внимание!")
            msgBox.setText("Пожалуйста, переключите раскладку клавиатуры на английскую, наш бот работает только с ней!")
            msgBox.exec()

    from pathlib import Path

    def send_stats(self):
        """
        Метод для отправки статистики:
          - Запускает скрипт screenshotstats.py (который делает скриншот),
          - Ждёт пару секунд,
          - Ищет созданный файл,
          - Отправляет его в Telegram,
          - При успешной отправке удаляет файл.
        """
        from pathlib import Path

        # Путь к скрипту screenshotstats.py (предполагается, что он находится в modules/OtherService/)
        screenshotstats_path = os.path.join(MODULES_BASE, "OtherService", "screenshotstats.py")
        if not os.path.exists(screenshotstats_path):
            print("Файл screenshotstats.py не найден.")
            return

        # Запускаем скрипт и ждём его завершения (блокирующий вызов)
        subprocess.run([PYTHON_EXEC, screenshotstats_path])

        # Добавляем задержку, чтобы убедиться, что файл записался
        time.sleep(2)

        # Папка, куда скрипт сохраняет скриншоты
        screenshot_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "resources", "screenshots"))
        from pathlib import Path
        screenshot_dir = Path(screenshot_dir)
        files = list(screenshot_dir.glob("screenshot_*.png"))

        # Для отладки выведите список найденных файлов
        print("Найденные файлы:", files)

        if not files:
            print("Скриншот не найден после выполнения скрипта.")
            return

        screenshot_file = max(files, key=lambda p: p.stat().st_mtime)
        if send_screenshot_to_telegram(str(screenshot_file)):
            os.remove(str(screenshot_file))
            print("Скриншот отправлен и удалён.")
        else:
            print("Ошибка отправки скриншота.")


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
        keyboard = [
            [KeyboardButton(" Anti-AFK"), KeyboardButton(" Авто-колесо"), KeyboardButton(" Лотерея")],
            [KeyboardButton(" Реконнект"), KeyboardButton(" Статистика")],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
        text = (
            "<b>Привет!</b> Я бот управления сервисами.\n"
            "Выберите действие, нажав кнопку внизу.\n\n"
            "<i>Список команд:</i>\n"
            "• Anti-AFK — запустить/остановить систему анти-АФК\n"
            "• Авто-колесо — провернуть колесо удачи\n"
            "• Лотерея — запустить/остановить лотерею\n"
            "• Реконнект — перезапустить игру при вылете\n"
            "• Статистика — сделать скриншот статистики и отправить его в Telegram\n"
        )
        update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

    dp.add_handler(CommandHandler("start", cmd_start))

    def msg_handler(update: Update, context: CallbackContext):
        global window
        text = update.message.text
        if text == " Anti-AFK":
            window.toggle_antiafk()
            status = "запущен" if window.processes["antiafk"] else "остановлен"
            update.message.reply_text(f"<b>Anti-AFK</b>: {status}", parse_mode=ParseMode.HTML)
        elif text == " Авто-колесо":
            if window.processes["koleso"] is None:
                window.toggle_koleso(True)
                update.message.reply_text(" <b>Авто-колесо</b> запущена.", parse_mode=ParseMode.HTML)
            else:
                window.toggle_koleso(False)
                update.message.reply_text(" <b>Авто-колесо</b> остановлена.", parse_mode=ParseMode.HTML)
        elif text == " Лотерея":
            if window.processes["lottery"] is None:
                window.toggle_lottery(True)
                update.message.reply_text(" <b>Лотерея</b> запущена.", parse_mode=ParseMode.HTML)
            else:
                window.toggle_lottery(False)
                update.message.reply_text("<b>Лотерея</b> остановлена.", parse_mode=ParseMode.HTML)
        elif text == " Реконнект":
            if window.manual_reconnect():
                update.message.reply_text(" <b>Реконнект</b> запущен немедленно.", parse_mode=ParseMode.HTML)
            else:
                update.message.reply_text("️ <b>Реконнект</b>: произошла ошибка.", parse_mode=ParseMode.HTML)
        elif text == " Статистика":
            window.send_stats()
            update.message.reply_text(" <b>Статистика</b> отправлена.", parse_mode=ParseMode.HTML)
        else:
            update.message.reply_text("Неизвестная команда. Нажмите /start, чтобы открыть меню.", parse_mode=ParseMode.HTML)

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, msg_handler))
    updater.start_polling()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # license_valid = False
    # expiry_date = load_license()
    # if expiry_date:
    #     now = datetime.datetime.now()
    #     if expiry_date > now:
    #         print(f" Подписка активна до {expiry_date}")
    #         license_valid = True
    #     else:
    #         print(" Подписка истекла. Требуется новый ключ!")
    # else:
    #     print(" Ключ не найден. Требуется активация!")
    # if not license_valid:
    #     license_dialog = QDialog()
    #     license_dialog.setWindowTitle("Аутентификация")
    #     license_dialog.setFixedSize(400, 300)
    #     layout = QVBoxLayout(license_dialog)
    #     logo_label = QLabel(" Введите лицензионный ключ")
    #     logo_label.setAlignment(Qt.AlignCenter)
    #     layout.addWidget(logo_label)
    #     key_input = QLineEdit()
    #     key_input.setPlaceholderText("Введите лицензионный ключ")
    #     layout.addWidget(key_input)
    #     activate_button = QPushButton("Активировать")
    #     layout.addWidget(activate_button)
    #     message_label = QLabel("")
    #     message_label.setAlignment(Qt.AlignCenter)
    #     message_label.setStyleSheet("color: #ff7043; font-size: 16px;")
    #     layout.addWidget(message_label)
    #     def on_activate():
    #         key = key_input.text().strip()
    #         success, expiry = validate_key(key)
    #         if success:
    #             save_license(key, expiry)
    #             message_label.setText(f" Активировано! Подписка до: {expiry}")
    #             license_dialog.accept()
    #         else:
    #             message_label.setText(" Ошибка активации. Проверьте ключ.")
    #     activate_button.clicked.connect(on_activate)
    #     if license_dialog.exec() != QDialog.Accepted:
    #         print(" Активация не завершена. Выход...")
    #         sys.exit(1)
    #     license_valid = True
    # if not license_valid:
    #     print(" Подписка недействительна. Запуск невозможен.")
    #     sys.exit(1)
    print(" Запуск основного приложения...")
    window = MainWindow()
    window.setWindowTitle("Менеджер сервисов бота")
    window.setGeometry(100, 100, 900, 600)
    window.show()
    tg_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    tg_thread.start()
    print(">>> Telegram-бот запущен (используйте /start)")
    sys.exit(app.exec())