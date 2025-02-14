import ctypes
import sys
import os
import subprocess
import datetime
import uuid
import platform
import hashlib
import requests  # Для связи с сервером
import json
import threading

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QStackedWidget, QPushButton, QLabel, QLineEdit, QCheckBox, QDialog, QSizePolicy, QMessageBox
)

# Сервер для проверки лицензий
SERVER_URL = "http://83.220.165.162:5000"

# Определяем базовый каталог – где находится main.py.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.isdir(os.path.join(BASE_DIR, "src")):
    PROJECT_ROOT = BASE_DIR
else:
    PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

# Файл лицензии и настроек
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

# Функции работы с настройками
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

# Определяем путь к папке modules
MODULES_BASE = None
if os.path.isdir(os.path.join(BASE_DIR, "modules")):
    MODULES_BASE = os.path.join(BASE_DIR, "modules")
elif os.path.isdir(os.path.join(BASE_DIR, "src", "modules")):
    MODULES_BASE = os.path.join(BASE_DIR, "src", "modules")
else:
    raise FileNotFoundError("Не найдена папка modules в BASE_DIR или BASE_DIR/src")

# Добавляем путь к модулю process_checker.
sys.path.append(os.path.join(MODULES_BASE, "ProcessChecker"))
import process_checker

# Пути до скриптов (оставьте как есть)
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
    print(f"📤 Отправляем на сервер:\n  Ключ: {key}\n  HWID: {hwid}")
    try:
        response = requests.post(f"{SERVER_URL}/validate", json={"key": key, "hwid": hwid})
        data = response.json()
        print(f"📥 Ответ сервера: {data}")
        if response.status_code == 200:
            expiry_date_str = data.get("expiry_date")
            expiry_date = datetime.datetime.strptime(expiry_date_str, "%Y-%m-%d %H:%M:%S")
            print(f"✅ Ключ действителен. Подписка до {expiry_date}")
            return True, expiry_date
        else:
            print(f"❌ Ошибка: {data.get('message', 'Unknown error')}")
            return False, None
    except requests.RequestException as e:
        print(f"❌ Ошибка подключения к серверу: {e}")
        return False, None

def load_license():
    if os.path.exists(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, "r") as f:
                license_info = json.load(f)
            stored_hwid = license_info.get("hwid")
            current_hwid = get_hwid()
            if stored_hwid != current_hwid:
                print("❌ HWID не совпадает! Требуется повторная активация.")
                return None
            expiry_date_str = license_info.get("expiry_date")
            if expiry_date_str:
                return datetime.datetime.strptime(expiry_date_str, "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(f"❌ Ошибка загрузки лицензии: {e}")
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
        print(f"💾 Лицензия сохранена: подписка до {expiry_date}")
    except Exception as e:
        print(f"❌ Ошибка при сохранении лицензии: {e}")

from PySide6.QtWidgets import QSizePolicy

class MainWindow(QMainWindow):
    instance = None
    def __init__(self):
        super().__init__()
        MainWindow.instance = self
        self.setWindowTitle("Менеджер сервисов бота")
        self.setGeometry(100, 100, 900, 600)
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
            "telegram_bot": None
        }

        self.start_telegram_bot_automatically()

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

        left_panel = QWidget()
        left_panel.setSizePolicy(left_panel.sizePolicy().horizontalPolicy(), QSizePolicy.Expanding)
        left_layout = QVBoxLayout(left_panel)
        self.menu_list = QListWidget()
        self.menu_list.setStyleSheet(
            "font-size: 18px;"
            "QListWidget::item:selected { background-color: #ff7043; border: 4px solid #ff7043; }"
        )
        self.menu_list.addItem("Anti-AFK")
        self.menu_list.addItem("Крафты")
        self.menu_list.addItem("Работы")
        self.menu_list.addItem("Пассивные функции")
        self.menu_list.addItem("Спортзал")
        self.menu_list.addItem("Контракты")
        self.menu_list.addItem("Настройки")
        self.menu_list.addItem("Телеграмм")
        self.menu_list.currentRowChanged.connect(self.switch_page)
        left_layout.addWidget(self.menu_list)

        self.license_label = QLabel()
        self.license_label.setStyleSheet("font-size: 14px; color: #ff7043;")
        left_layout.addWidget(self.license_label)
        left_layout.setAlignment(self.license_label, Qt.AlignBottom)
        main_layout.addWidget(left_panel, 1)

        self.pages = QStackedWidget()
        self.page_antiafk = self.create_antiafk_page()
        self.page_cook = self.create_cook_page()
        self.page_work = self.create_work_page()
        self.page_automood = self.create_automood_page()
        self.page_sportzal = self.create_sportzal_page()
        self.page_contracts = self.create_contracts_page()
        self.page_settings = self.create_settings_page()
        self.tg_page = self.create_tg_page()
        self.pages.addWidget(self.page_antiafk)
        self.pages.addWidget(self.page_cook)
        self.pages.addWidget(self.page_work)
        self.pages.addWidget(self.page_automood)
        self.pages.addWidget(self.page_sportzal)
        self.pages.addWidget(self.page_contracts)
        self.pages.addWidget(self.page_settings)
        self.pages.addWidget(self.tg_page)
        main_layout.addWidget(self.pages, 3)
        self.switch_page(0)

        self.game_timer = QTimer(self)
        self.game_timer.timeout.connect(self.check_game_active)
        self.game_timer.start(1000)

        self.license_timer = QTimer(self)
        self.license_timer.timeout.connect(self.update_license_label)
        self.license_timer.start(1000)

    def telegram_toggle_antiafk(self):
        self.toggle_antiafk()

    def check_keyboard_layout(self):
        if get_keyboard_layout() != LANG_ENGLISH:
            QMessageBox.warning(self, "Внимание!",
                                "Пожалуйста, переключите раскладку клавиатуры на английскую, наш бот работает только с ней!")

    def periodic_license_check(self):
        if self.license_expiry:
            now = datetime.datetime.now()
            if now >= self.license_expiry:
                print("❌ Лицензия истекла. Завершение работы приложения.")
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

    def create_work_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        title = QLabel("Work Service")
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
        self.skolzkaya_button = QPushButton("Запустить Схемы")
        self.skolzkaya_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.skolzkaya_button.clicked.connect(self.toggle_skolzkaya)
        layout.addWidget(self.skolzkaya_button)
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
        self.automood_key_input.setPlaceholderText("Введите клавишу, например: L (работают только Eng - раскладка)")
        self.automood_key_input.setStyleSheet("font-size: 16px; padding: 5px;")
        layout.addWidget(self.automood_key_input)
        self.automood_launch_button = QPushButton("Запустить Авто-Настроение")
        self.automood_launch_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.automood_launch_button.clicked.connect(self.toggle_automood)
        layout.addWidget(self.automood_launch_button)
        autorun_instr = QLabel("Настройте функцию Авто-Бег (эмуляция нажатия выбранной клавиши для бега).")
        autorun_instr.setAlignment(Qt.AlignCenter)
        layout.addWidget(autorun_instr)
        autorun_label = QLabel("Клавиша Авто-Бег:")
        autorun_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(autorun_label)
        self.autorun_key_input = QLineEdit()
        self.autorun_key_input.setPlaceholderText("Введите клавишу, например: J (работают только Eng - раскладка)")
        self.autorun_key_input.setStyleSheet("font-size: 16px; padding: 5px;")
        layout.addWidget(self.autorun_key_input)
        self.autorun_launch_button = QPushButton("Запустить Авто-Бег")
        self.autorun_launch_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.autorun_launch_button.clicked.connect(self.toggle_autorun)
        layout.addWidget(self.autorun_launch_button)
        autoeat_instr = QLabel("Настройте функцию Авто-Еда (эмуляция нажатия выбранной клавиши при обнаружении недостатка еды).")
        autoeat_instr.setAlignment(Qt.AlignCenter)
        layout.addWidget(autoeat_instr)
        autoeat_label = QLabel("Клавиша Авто-Еда:")
        autoeat_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(autoeat_label)
        self.autoeat_key_input = QLineEdit()
        self.autoeat_key_input.setPlaceholderText("Введите клавишу, например: H (работают только Eng - раскладка)")
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

    def create_sportzal_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        title = QLabel("Спортзал")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px;")
        layout.addWidget(title)
        desc = QLabel("Запустите программу для тренировки мышц. Функция будет эмулировать действия в спортзале.")
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
        desc = QLabel("Введите путь до файла Rage MP (exe), который будет запускаться.")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 16px;")
        layout.addWidget(desc)
        path_label = QLabel("Путь до Rage MP:")
        path_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(path_label)
        self.rage_mp_path_input = QLineEdit()
        self.rage_mp_path_input.setPlaceholderText("Например: C:\\Program Files\\RageMP\\RageMP.exe")
        self.rage_mp_path_input.setStyleSheet("font-size: 16px; padding: 5px;")
        layout.addWidget(self.rage_mp_path_input)
        settings = load_settings()
        current_path = settings.get("rage_mp_path", "")
        self.rage_mp_path_input.setText(current_path)
        self.launch_game_button = QPushButton("Запустить игру")
        self.launch_game_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.launch_game_button.clicked.connect(self.toggle_launch_game)
        layout.addWidget(self.launch_game_button)
        self.settings_save_button = QPushButton("Сохранить настройки")
        self.settings_save_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.settings_save_button.clicked.connect(self.save_settings_page)
        layout.addWidget(self.settings_save_button)
        layout.addStretch()
        return widget

    def create_tg_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        title = QLabel("Telegram")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px;")
        layout.addWidget(title)
        desc = QLabel("Введите токен вашего Telegram бота и Chat ID, затем сохраните настройки. При запуске приложения, если настройки заданы, бот автоматически отправит сообщение об успешной авторизации.")
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
            self.work_hint_label.setText(f"Настройки сохранены: Automood = {automood_key}, Autorun = {autorun_key}, Autoeat = {autoeat_key}")
        else:
            self.work_hint_label.setText("Ошибка: введите корректные клавиши")

    def toggle_kosyaki(self):
        if self.processes.get("kosyaki") is None:
            wd = os.path.dirname(KOSYAKI_PATH)
            try:
                proc = subprocess.Popen([PYTHON_EXEC, KOSYAKI_PATH], cwd=wd)
                self.processes["kosyaki"] = proc
                self.kosyaki_button.setText("Остановить создание Косяков")
                self.kosyaki_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Скрипт kosyaki запущен, PID:", proc.pid)
            except Exception as e:
                print("Ошибка при запуске скрипта kosyaki:", e)
        else:
            try:
                self.processes["kosyaki"].terminate()
                self.processes["kosyaki"].wait()
                self.processes["kosyaki"] = None
                self.kosyaki_button.setText("Запустить создание Косяков")
                self.kosyaki_button.setStyleSheet("font-size: 16px; padding: 10px;")
                print("Скрипт kosyaki остановлен.")
            except Exception as e:
                print("Ошибка при остановке скрипта kosyaki:", e)

    def toggle_automood(self):
        if self.processes.get("automood") is None:
            wd = os.path.dirname(AUTOMOOD_PATH)
            try:
                proc = subprocess.Popen([PYTHON_EXEC, AUTOMOOD_PATH], cwd=wd)
                self.processes["automood"] = proc
                self.automood_launch_button.setText("Остановить Авто-Настроение")
                self.automood_launch_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Automood запущен, PID:", proc.pid)
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
        if self.processes.get("autorun") is None:
            wd = os.path.dirname(AUTORUN_PATH)
            try:
                proc = subprocess.Popen([PYTHON_EXEC, AUTORUN_PATH], cwd=wd)
                self.processes["autorun"] = proc
                self.autorun_launch_button.setText("Остановить Авто-Бег")
                self.autorun_launch_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Autorun запущен, PID:", proc.pid)
            except Exception as e:
                print("Ошибка при запуске Autorun:", e)
        else:
            try:
                self.processes["autorun"].terminate()
                self.processes["autorun"].wait()
                self.processes["autorun"] = None
                self.autorun_launch_button.setText("Запустить Авто-Бег")
                self.autorun_launch_button.setStyleSheet("font-size: 16px; padding: 10px;")
                print("Autorun остановлен.")
            except Exception as e:
                print("Ошибка при остановке Autorun:", e)

    def toggle_autoeat(self):
        if self.processes.get("autoeat") is None:
            wd = os.path.dirname(AUTOEAT_PATH)
            try:
                proc = subprocess.Popen([PYTHON_EXEC, AUTOEAT_PATH], cwd=wd)
                self.processes["autoeat"] = proc
                self.autoeat_launch_button.setText("Остановить Авто-Еда")
                self.autoeat_launch_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Autoeat запущен, PID:", proc.pid)
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
        print("toggle_koleso toggled:", checked)
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
        print("toggle_lottery toggled:", checked)
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
        if self.processes["cook"] is None:
            try:
                dish_count = int(self.cook_input.text())
                self.cook_error_label.setText("")
            except ValueError:
                self.cook_error_label.setText("Введите корректное число")
                return
            self.processes["cook"] = subprocess.Popen([PYTHON_EXEC, COOK_PATH, str(dish_count)], cwd=PROJECT_ROOT)
            self.cook_button.setText("Остановить")
            self.cook_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
        else:
            self.processes["cook"].terminate()
            self.processes["cook"].wait()
            self.processes["cook"] = None
            self.cook_button.setText("Запустить")
            self.cook_button.setStyleSheet("font-size: 16px; padding: 10px;")

    def toggle_waxta(self):
        if self.processes["waxta"] is None:
            wd = os.path.dirname(WAXTA_PATH)
            try:
                proc = subprocess.Popen([PYTHON_EXEC, WAXTA_PATH], cwd=wd)
                self.processes["waxta"] = proc
                self.waxta_button.setText("Остановить работу на Шахте")
                self.waxta_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Waxta запущена, PID:", proc.pid)
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
            wd = os.path.dirname(PORT_PATH)
            try:
                proc = subprocess.Popen([PYTHON_EXEC, PORT_PATH], cwd=wd)
                self.processes["port"] = proc
                self.port_button.setText("Остановить работу в Порту")
                self.port_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Port запущена, PID:", proc.pid)
            except Exception as e:
                print("Ошибка при запуске Port:", e)
        else:
            try:
                self.processes["port"].terminate()
                self.processes["port"].wait()
                self.processes["port"] = None
                self.port_button.setText("Запустить работу в Порту")
                self.port_button.setStyleSheet("font-size: 16px; padding: 10px;")
                print("Port остановлена.")
            except Exception as e:
                print("Ошибка при остановке Port:", e)

    def toggle_stroyka(self):
        if self.processes["stroyka"] is None:
            wd = os.path.dirname(STROYKA_PATH)
            try:
                proc = subprocess.Popen([PYTHON_EXEC, STROYKA_PATH], cwd=wd)
                self.processes["stroyka"] = proc
                self.stroyka_button.setText("Остановить работу на Стройке")
                self.stroyka_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Стройка запущена, PID:", proc.pid)
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
            wd = os.path.dirname(KOZLODOY_PATH)
            try:
                proc = subprocess.Popen([PYTHON_EXEC, KOZLODOY_PATH], cwd=wd)
                self.processes["kozlodoy"] = proc
                self.kozlodoy_button.setText("Остановить работу на Ферме")
                self.kozlodoy_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Работа на Ферме запущена, PID:", proc.pid)
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
        if self.processes.get("taxi") is None:
            wd = os.path.dirname(TAXI_PATH)
            try:
                proc = subprocess.Popen([PYTHON_EXEC, TAXI_PATH], cwd=wd)
                self.processes["taxi"] = proc
                self.taxi_button.setText("Остановить работу Таксистом")
                self.taxi_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Taxi запущен, PID:", proc.pid)
            except Exception as e:
                print("Ошибка при запуске Taxi:", e)
        else:
            try:
                self.processes["taxi"].terminate()
                self.processes["taxi"].wait()
                self.processes["taxi"] = None
                self.taxi_button.setText("Запустить работу Таксистом")
                self.taxi_button.setStyleSheet("font-size: 16px; padding: 10px;")
                print("Taxi остановлен.")
            except Exception as e:
                print("Ошибка при остановке Taxi:", e)

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
            wd = os.path.dirname(KACHALKA_PATH)
            try:
                proc = subprocess.Popen([PYTHON_EXEC, KACHALKA_PATH], cwd=wd)
                self.processes["kachalka"] = proc
                self.kachalka_launch_button.setText("Остановить Спортзал")
                self.kachalka_launch_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Спортзал запущен (kachalka), PID:", proc.pid)
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
            wd = os.path.dirname(SHVEIKA_PATH)
            try:
                proc = subprocess.Popen([PYTHON_EXEC, SHVEIKA_PATH], cwd=wd)
                self.processes["shveika"] = proc
                self.shveika_button.setText("Остановить пошив Одежды")
                self.shveika_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Shveika запущен, PID:", proc.pid)
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
                self.skolzkaya_button.setText("Остановить Схемы")
                self.skolzkaya_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Skolzkaya запущен, PID:", proc.pid)
            except Exception as e:
                print("Ошибка при запуске Skolzkaya:", e)
        else:
            try:
                self.processes["skolzkaya"].terminate()
                self.processes["skolzkaya"].wait()
                self.processes["skolzkaya"] = None
                self.skolzkaya_button.setText("Запустить Схемы")
                self.skolzkaya_button.setStyleSheet("font-size: 16px; padding: 10px;")
                print("Skolzkaya остановлен.")
            except Exception as e:
                print("Ошибка при остановке Skolzkaya:", e)

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
            settings["rage_mp_path"] = rage_mp_path
            save_settings(settings)
            self.work_hint_label.setText(f"Настройки сохранены: Rage MP = {rage_mp_path}")
        else:
            self.work_hint_label.setText("Ошибка: введите корректный путь до Rage MP")

    def toggle_launch_game(self):
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

    def start_telegram_bot_automatically(self):
        # Загружаем настройки (включая токен и chat id) из settings.json
        settings = load_settings()
        token = settings.get("telegram_token", "")
        chat_id = settings.get("telegram_chat_id", "")
        if token and chat_id:
            try:
                telegram_bot_path = os.path.join(MODULES_BASE, "TelegramService", "telegram_bot.py")
                if os.path.exists(telegram_bot_path):
                    wd = os.path.dirname(telegram_bot_path)
                    proc = subprocess.Popen([PYTHON_EXEC, telegram_bot_path, token], cwd=wd)
                    self.processes["telegram_bot"] = proc
                    print("Telegram бот запущен, PID:", proc.pid)
                else:
                    print("telegram_bot.py не найден – пропускаем запуск скрипта.")
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                payload = {"chat_id": chat_id, "text": "Авторизация успешна, Telegram бот запущен."}
                response = requests.post(url, data=payload)
                if response.status_code == 200:
                    print("Сообщение отправлено в Telegram.")
                else:
                    print(f"Ошибка отправки сообщения: {response.text}")
            except Exception as e:
                print(f"Ошибка при автоматическом запуске Telegram бота: {e}")

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
        self.kozlodoy_button.setText("Запустить Козлодой")
        self.kozlodoy_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.chk_koleso.setChecked(False)
        self.chk_lottery.setChecked(False)
        if hasattr(self, 'chk_autorun'):
            self.chk_autorun.setChecked(False)
        self.work_hint_label.setText("")

from flask import Flask, request

api_app = Flask(__name__)

@api_app.route('/antiafk', methods=['POST'])
def antiafk_endpoint():
    from datetime import datetime
    if MainWindow.instance and MainWindow.instance.license_expiry and MainWindow.instance.license_expiry > datetime.now():
        MainWindow.instance.toggle_antiafk()
        return "Anti-AFK переключён", 200
    return "Лицензия недействительна или приложение не готово", 403

@api_app.route('/cook', methods=['POST'])
def cook_endpoint():
    if MainWindow.instance:
        dish_count = request.form.get('dish_count', '1')
        try:
            int(dish_count)
        except ValueError:
            return "Некорректное число блюд", 400
        MainWindow.instance.cook_input.setText(dish_count)
        MainWindow.instance.toggle_cook()
        return "Крафты переключены", 200
    return "Приложение не готово", 500

def run_api_server():
    api_app.run(host='127.0.0.1', port=5000)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    license_valid = False
    expiry_date = load_license()

    if expiry_date:
        now = datetime.datetime.now()
        if expiry_date > now:
            print(f"✅ Подписка активна до {expiry_date}")
            license_valid = True
        else:
            print("❌ Подписка истекла. Требуется новый ключ!")
    else:
        print("❌ Ключ не найден. Требуется активация!")

    if not license_valid:
        license_dialog = QDialog()
        license_dialog.setWindowTitle("Аутентификация")
        license_dialog.setFixedSize(400, 300)
        layout = QVBoxLayout(license_dialog)
        logo_label = QLabel("🔑 Введите лицензионный ключ")
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)
        key_input = QLineEdit()
        key_input.setPlaceholderText("Введите лицензионный ключ")
        layout.addWidget(key_input)
        activate_button = QPushButton("Активировать")
        layout.addWidget(activate_button)
        message_label = QLabel("")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("color: #ff7043; font-size: 16px;")
        layout.addWidget(message_label)

        def on_activate():
            key = key_input.text().strip()
            success, expiry = validate_key(key)
            if success:
                save_license(key, expiry)
                message_label.setText(f"✅ Активировано! Подписка до: {expiry}")
                license_dialog.accept()
            else:
                message_label.setText("❌ Ошибка активации. Проверьте ключ.")

        activate_button.clicked.connect(on_activate)

        if license_dialog.exec() != QDialog.Accepted:
            print("❌ Активация не завершена. Выход...")
            sys.exit(1)

        license_valid = True

    if not license_valid:
        print("❌ Подписка недействительна. Запуск невозможен.")
        sys.exit(1)

    print("🚀 Запуск основного приложения...")
    window = MainWindow()
    window.setWindowTitle("Менеджер сервисов бота")
    window.setGeometry(100, 100, 900, 600)
    window.show()

    threading.Thread(target=run_api_server, daemon=True).start()

    sys.exit(app.exec())
