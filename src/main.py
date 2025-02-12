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
SERVER_URL = "http://83.220.165.162:5000"

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
    """Проверяет ключ через сервер."""
    hwid = get_hwid()
    print(f"📤 Отправляем на сервер:\n  Ключ: {key}\n  HWID: {hwid}")  # Вывод перед отправкой

    try:
        response = requests.post(f"{SERVER_URL}/validate", json={"key": key, "hwid": hwid})
        data = response.json()
        print(f"📥 Ответ сервера: {data}")  # Лог ответа сервера

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


########################################################################
# Функции загрузки и сохранения лицензии
########################################################################

def load_license():
    """Загружает локальный ключ лицензии."""
    if os.path.exists(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, "r") as f:
                license_info = json.load(f)

            expiry_date_str = license_info.get("expiry_date")
            if expiry_date_str:
                return datetime.datetime.strptime(expiry_date_str, "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(f"❌ Ошибка загрузки лицензии: {e}")
    return None


def save_license(key, expiry_date):
    """Сохраняет лицензию локально."""
    license_info = {
        "key": key,
        "hwid": get_hwid(),
        "expiry_date": expiry_date.strftime("%Y-%m-%d %H:%M:%S")  # Сохраняем в виде строки
    }
    with open(LICENSE_FILE, "w") as f:
        json.dump(license_info, f)
    print(f"💾 Лицензия сохранена: подписка до {expiry_date}")


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
    app = QApplication(sys.argv)
    license_valid = False

    # 1️⃣ Загружаем сохранённую лицензию
    expiry_date = load_license()

    # 2️⃣ Проверяем подписку
    if expiry_date:
        now = datetime.datetime.now()
        if expiry_date > now:
            print(f"✅ Подписка активна до {expiry_date}")
            license_valid = True
        else:
            print("❌ Подписка истекла. Требуется новый ключ!")
    else:
        print("❌ Ключ не найден. Требуется активация!")

    # 3️⃣ Если подписка недействительна, запрашиваем ключ у пользователя
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
                save_license(key, expiry)  # Сохраняем лицензию
                message_label.setText(f"✅ Активировано! Подписка до: {expiry}")
                license_dialog.accept()
            else:
                message_label.setText("❌ Ошибка активации. Проверьте ключ.")

        activate_button.clicked.connect(on_activate)

        if license_dialog.exec() != QDialog.Accepted:
            print("❌ Активация не завершена. Выход...")
            sys.exit(1)

        # Обновляем переменную, раз лицензия теперь действительна
        license_valid = True

    # 4️⃣ Если подписка активна, запускаем основное окно приложения
    if not license_valid:
        print("❌ Подписка недействительна. Запуск невозможен.")
        sys.exit(1)

    print("🚀 Запуск основного приложения...")
    window = MainWindow()
    window.setWindowTitle("Менеджер сервисов бота")
    window.setGeometry(100, 100, 900, 600)
    window.show()

    sys.exit(app.exec())


