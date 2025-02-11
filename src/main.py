import sys
import os
import subprocess
import datetime
import uuid
import platform
import hashlib
import requests  # Для связи с сервером
import json

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QStackedWidget, QPushButton, QLabel, QLineEdit, QCheckBox, QDialog
)

# Сервер для проверки лицензий
SERVER_URL = "http://127.0.0.1:5000"

# Определяем базовый каталог – где находится main.py.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if os.path.isdir(os.path.join(BASE_DIR, "src")):
    PROJECT_ROOT = BASE_DIR
else:
    PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

if os.path.isdir(os.path.join(BASE_DIR, "modules")):
    MODULES_BASE = os.path.join(BASE_DIR, "modules")
elif os.path.isdir(os.path.join(BASE_DIR, "src", "modules")):
    MODULES_BASE = os.path.join(BASE_DIR, "src", "modules")
else:
    raise FileNotFoundError("Не найдена папка modules в BASE_DIR или BASE_DIR/src")

# Файл лицензии
LICENSE_FILE = os.path.join(PROJECT_ROOT, "license.dat")

# Добавляем путь к модулю process_checker.
sys.path.append(os.path.join(MODULES_BASE, "ProcessChecker"))
import process_checker

# Абсолютные пути до скриптов (ботов)
ANTIAFK_PATH     = os.path.join(MODULES_BASE, "AntiAfkService", "antiafk.py")
KRUTKAKOLES_PATH = os.path.join(MODULES_BASE, "AntiAfkService", "krutkakoles.py")
LOTTERY_PATH     = os.path.join(MODULES_BASE, "AntiAfkService", "lottery.py")
COOK_PATH        = os.path.join(MODULES_BASE, "CraftService", "cook.py")
WAXTA_PATH       = os.path.join(MODULES_BASE, "WorkService", "waxta.py")
PORT_PATH        = os.path.join(MODULES_BASE, "WorkService", "port.py")
STROYKA_PATH     = os.path.join(MODULES_BASE, "WorkService", "stroyka.py")
KOZLODOY_PATH    = os.path.join(MODULES_BASE, "WorkService", "kozlodoy.py")
AUTORUN_PATH     = os.path.join(MODULES_BASE, "OtherService", "autorun.py")

# Используем sys.executable для запуска того же интерпретатора.
PYTHON_EXEC = sys.executable

########################################################################
# Функции для идентификации устройства
########################################################################

def get_device_id():
    """Возвращает MAC-адрес в виде шестнадцатеричной строки."""
    return hex(uuid.getnode())

def get_hwid():
    """
    Вычисляет дополнительный уникальный идентификатор (HWID) на основе:
      - MAC-адреса,
      - Имени компьютера (из переменной окружения COMPUTERNAME),
      - Информации о процессоре.
    """
    mac = str(uuid.getnode())
    computer_name = os.environ.get('COMPUTERNAME', 'unknown')
    processor = platform.processor()
    combined = mac + computer_name + processor
    return hashlib.sha256(combined.encode()).hexdigest()

########################################################################
# Функция проверки ключа
########################################################################

def validate_key(key: str):
    """Проверяет ключ через сервер"""
    hwid = get_hwid()
    try:
        response = requests.post(f"{SERVER_URL}/validate", json={"key": key, "hwid": hwid})
        data = response.json()
        if response.status_code == 200:
            return True, data.get("expiry_date")
        else:
            print(f"Ошибка: {data.get('message', 'Unknown error')}")
            return False, None
    except requests.RequestException as e:
        print(f"Ошибка подключения к серверу: {e}")
        return False, None

########################################################################
# Лицензионный диалог
########################################################################

class LicenseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Аутентификация")
        self.setFixedSize(400, 300)
        layout = QVBoxLayout(self)

        # Логотип (можно заменить изображением)
        self.logo_label = QLabel("LOGO")
        self.logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo_label)

        # Поле ввода ключа
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Введите лицензионный ключ")
        layout.addWidget(self.key_input)

        # Кнопка активации
        self.activate_button = QPushButton("Активировать")
        layout.addWidget(self.activate_button)
        self.activate_button.clicked.connect(self.activate)

        # Сообщение об ошибке/подтверждении
        self.message_label = QLabel("")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("color: #ff7043; font-size: 16px;")
        layout.addWidget(self.message_label)

        # Таймер подписки (показывает оставшееся время)
        self.timer_label = QLabel("")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(self.timer_label)

        self.expiry_date = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

    def activate(self):
        key = self.key_input.text().strip()
        success, expiry_date = validate_key(key)
        if success:
            save_license(key, expiry_date)
            self.message_label.setText(f"Активировано! Подписка до: {expiry_date}")
            self.accept()
        else:
            self.message_label.setText("Ошибка активации. Проверьте ключ.")

    def update_timer(self):
        if self.expiry_date is None:
            return
        now = datetime.datetime.now()
        remaining = self.expiry_date - now
        if remaining.total_seconds() <= 0:
            self.timer_label.setText("Подписка истекла")
            self.timer.stop()
        else:
            self.timer_label.setText(f"Осталось: {str(remaining).split('.')[0]}")

########################################################################
# Функции загрузки и сохранения лицензии
########################################################################

def load_license():
    """Проверяет локальный ключ и валидирует его через сервер"""
    if os.path.exists(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, "r") as f:
                license_info = json.load(f)
            key = license_info.get("key")
            saved_hwid = license_info.get("hwid")

            if key and saved_hwid:
                success, expiry_date = validate_key(key)
                if success:
                    return expiry_date
                else:
                    print("Ключ недействителен. Перезапросите активацию.")
                    return None
        except Exception as e:
            print(f"Ошибка загрузки лицензии: {e}")
    return None

def save_license(key, expiry_date):
    """Сохраняет лицензию локально"""
    license_info = {
        "key": key,
        "hwid": get_hwid(),
        "expiry_date": expiry_date
    }
    with open(LICENSE_FILE, "w") as f:
        json.dump(license_info, f)


########################################################################
# Основное окно приложения
########################################################################

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
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
            "autorun": None
        }
        self.inactive_counter = 0
        self.bots_killed_due_to_inactivity = False

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        self.menu_list = QListWidget()
        self.menu_list.setStyleSheet(
            "font-size: 18px;"
            "QListWidget::item:selected { background-color: #ff7043; border: 4px solid #ff7043; }"
        )
        self.menu_list.addItem("Anti-AFK")
        self.menu_list.addItem("Готовка")
        self.menu_list.addItem("Работы")
        self.menu_list.currentRowChanged.connect(self.switch_page)
        main_layout.addWidget(self.menu_list, 1)

        self.pages = QStackedWidget()
        self.page_antiafk = self.create_antiafk_page()
        self.page_cook = self.create_cook_page()
        self.page_work = self.create_work_page()
        self.pages.addWidget(self.page_antiafk)
        self.pages.addWidget(self.page_cook)
        self.pages.addWidget(self.page_work)
        main_layout.addWidget(self.pages, 3)
        self.switch_page(0)

        self.game_timer = QTimer(self)
        self.game_timer.timeout.connect(self.check_game_active)
        self.game_timer.start(1000)

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
        self.chk_koleso = QCheckBox("Крутка колеса")
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
        title = QLabel("Готовка")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px;")
        layout.addWidget(title)
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
        self.kozlodoy_button = QPushButton("Запустить Козлодой")
        self.kozlodoy_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.kozlodoy_button.clicked.connect(self.toggle_kozlodoy)
        layout.addWidget(self.kozlodoy_button)
        self.chk_autorun = QCheckBox("Autorun")
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

    def toggle_antiafk(self):
        if self.processes["antiafk"] is None:
            self.processes["antiafk"] = subprocess.Popen(
                [PYTHON_EXEC, ANTIAFK_PATH],
                cwd=PROJECT_ROOT
            )
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
                proc = subprocess.Popen(
                    [PYTHON_EXEC, KRUTKAKOLES_PATH],
                    cwd=wd,
                )
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
                proc = subprocess.Popen(
                    [PYTHON_EXEC, LOTTERY_PATH],
                    cwd=wd,
                )
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
            self.processes["cook"] = subprocess.Popen(
                [PYTHON_EXEC, COOK_PATH, str(dish_count)],
                cwd=PROJECT_ROOT,
            )
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
                proc = subprocess.Popen(
                    [PYTHON_EXEC, WAXTA_PATH],
                    cwd=wd,
                )
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
                proc = subprocess.Popen(
                    [PYTHON_EXEC, PORT_PATH],
                    cwd=wd,
                )
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
                proc = subprocess.Popen(
                    [PYTHON_EXEC, STROYKA_PATH],
                    cwd=wd,
                )
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
                proc = subprocess.Popen(
                    [PYTHON_EXEC, KOZLODOY_PATH],
                    cwd=wd,
                )
                self.processes["kozlodoy"] = proc
                self.kozlodoy_button.setText("Остановить Козлодой")
                self.kozlodoy_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #ff7043; color: white;")
                print("Козлодой запущен, PID:", proc.pid)
            except Exception as e:
                print("Ошибка при запуске Козлодоя:", e)
        else:
            try:
                self.processes["kozlodoy"].terminate()
                self.processes["kozlodoy"].wait()
                self.processes["kozlodoy"] = None
                self.kozlodoy_button.setText("Запустить Козлодой")
                self.kozlodoy_button.setStyleSheet("font-size: 16px; padding: 10px;")
                print("Козлодой остановлен.")
            except Exception as e:
                print("Ошибка при остановке Козлодоя:", e)

    def toggle_autorun(self, checked):
        print("toggle_autorun toggled:", checked)
        if checked:
            wd = os.path.dirname(AUTORUN_PATH)
            try:
                proc = subprocess.Popen(
                    [PYTHON_EXEC, AUTORUN_PATH],
                    cwd=wd,
                )
                self.processes["autorun"] = proc
                self.work_hint_label.setText("Клавиша для активации Autorun - +/=")
                print("Autorun запущен, PID:", proc.pid)
            except Exception as e:
                print("Ошибка при запуске Autorun:", e)
        else:
            if self.processes.get("autorun") is not None:
                try:
                    self.processes["autorun"].terminate()
                    self.processes["autorun"].wait()
                    print("Autorun остановлен.")
                except Exception as e:
                    print("Ошибка при остановке Autorun:", e)
                self.processes["autorun"] = None
                self.work_hint_label.setText("")

    def check_game_active(self):
        if process_checker.is_game_active():
            self.inactive_counter = 0
            self.bots_killed_due_to_inactivity = False
        else:
            self.inactive_counter += 1
            print(f"Игра не активна уже {self.inactive_counter} секунд.")
            if self.inactive_counter >= 180 and not self.bots_killed_due_to_inactivity:
                print("Игра не активна 3 минуты. Останавливаем всех ботов.")
                self.kill_all_bots()
                self.bots_killed_due_to_inactivity = True

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
        self.chk_autorun.setChecked(False)
        self.work_hint_label.setText("")


if __name__ == "__main__":
    import json
    import requests

    SERVER_URL = "http://127.0.0.1:5000"  # Сервер проверки лицензий
    license_valid = False
    expiry_date = None


    def validate_key(key: str):
        """Проверяет ключ на сервере"""
        hwid = get_hwid()
        try:
            response = requests.post(f"{SERVER_URL}/validate", json={"key": key, "hwid": hwid})
            data = response.json()
            if response.status_code == 200:
                return True, data.get("expiry_date")
            else:
                print(f"Ошибка: {data.get('message', 'Unknown error')}")
                return False, None
        except requests.RequestException as e:
            print(f"Ошибка подключения к серверу: {e}")
            return False, None


    expiry_date = load_license()
    if expiry_date and expiry_date > datetime.datetime.now():
        license_valid = True

    app = QApplication(sys.argv)

    if not license_valid:
        license_dialog = QDialog()
        license_dialog.setWindowTitle("Аутентификация")
        license_dialog.setFixedSize(400, 300)
        ld_layout = QVBoxLayout(license_dialog)
        logo_label = QLabel("LOGO")
        logo_label.setAlignment(Qt.AlignCenter)
        ld_layout.addWidget(logo_label)
        key_input = QLineEdit()
        key_input.setPlaceholderText("Введите лицензионный ключ")
        ld_layout.addWidget(key_input)
        activate_button = QPushButton("Активировать")
        ld_layout.addWidget(activate_button)
        message_label = QLabel("")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("color: #ff7043; font-size: 16px;")
        ld_layout.addWidget(message_label)
        timer_label = QLabel("")
        timer_label.setAlignment(Qt.AlignCenter)
        timer_label.setStyleSheet("font-size: 16px;")
        ld_layout.addWidget(timer_label)


        def on_activate():
            key = key_input.text().strip()
            success, expiry = validate_key(key)
            if success:
                save_license(key, expiry)
                message_label.setText(f"Активировано! Подписка до: {expiry}")
                license_dialog.accept()
            else:
                message_label.setText("Ошибка активации. Проверьте ключ.")


        activate_button.clicked.connect(on_activate)

        if license_dialog.exec() != QDialog.Accepted:
            sys.exit(0)

    window = MainWindow()
    window.show()
    window.inactive_counter = 0
    result = app.exec()
    sys.exit(result)

