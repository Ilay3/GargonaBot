import sys
import os
import subprocess
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QComboBox, QLineEdit, QCheckBox
)
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Automation App")
        self.setFixedSize(900, 600)

        # Переменная для процесса Anti AFK
        self.anti_afk_process = None

        # Основной виджет и горизонтальный layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Левый сайдбар (меню)
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("background-color: #2c2c2c;")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(10)

        # Кнопки меню – плоские, с меньшим шрифтом и узкими отступами
        self.btn_anti_afk = QPushButton("Anti AFK")
        self.btn_cook = QPushButton("Cook")
        for btn in (self.btn_anti_afk, self.btn_cook):
            btn.setFlat(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    color: white;
                    background-color: transparent;
                    border: none;
                    font-size: 16px;
                    text-align: left;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #3a3a3a;
                }
                QPushButton:pressed {
                    background-color: #444444;
                }
            """)
            sidebar_layout.addWidget(btn)
        sidebar_layout.addStretch()

        # Правая панель – переключаемые страницы
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #f0f0f0;")

        # ===== Страница Anti AFK =====
        self.page_anti_afk = QWidget()
        anti_afk_layout = QVBoxLayout(self.page_anti_afk)
        anti_afk_layout.setContentsMargins(20, 20, 20, 20)
        anti_afk_layout.setSpacing(10)
        anti_afk_layout.setAlignment(Qt.AlignTop)

        label_anti_afk = QLabel("Anti AFK")
        label_anti_afk.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        anti_afk_layout.addWidget(label_anti_afk)

        btn_start = QPushButton("Запустить")
        btn_start.setFlat(True)
        btn_start.setStyleSheet("""
            QPushButton {
                color: #333;
                background-color: #e0e0e0;
                border: 1px solid #ccc;
                font-size: 16px;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QPushButton:pressed {
                background-color: #c0c0c0;
            }
        """)
        btn_start.clicked.connect(self.startAntiAFK)
        anti_afk_layout.addWidget(btn_start)

        # Горизонтальный layout для "Лотерея" и переключателя, выровненных по правому краю
        lottery_layout = QHBoxLayout()
        lottery_label = QLabel("Лотерея")
        lottery_label.setStyleSheet("font-size: 16px; color: #333;")
        lottery_layout.addWidget(lottery_label)
        lottery_layout.addStretch()
        self.lottery_switch = QCheckBox()
        self.lottery_switch.setStyleSheet("""
            QCheckBox::indicator {
                width: 40px;
                height: 20px;
                border-radius: 10px;
                background-color: #ccc;
            }
            QCheckBox::indicator:checked {
                background-color: #4cd964;
            }
        """)
        lottery_layout.addWidget(self.lottery_switch)
        anti_afk_layout.addLayout(lottery_layout)

        btn_stop = QPushButton("Остановить")
        btn_stop.setFlat(True)
        btn_stop.setStyleSheet("""
            QPushButton {
                color: #333;
                background-color: #e0e0e0;
                border: 1px solid #ccc;
                font-size: 16px;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QPushButton:pressed {
                background-color: #c0c0c0;
            }
        """)
        btn_stop.clicked.connect(self.stopAntiAFK)
        anti_afk_layout.addWidget(btn_stop)

        # ===== Страница Cook =====
        self.page_cook = QWidget()
        cook_layout = QVBoxLayout(self.page_cook)
        cook_layout.setContentsMargins(20, 20, 20, 20)
        cook_layout.setSpacing(10)
        cook_layout.setAlignment(Qt.AlignTop)

        label_cook = QLabel("Cook")
        label_cook.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        cook_layout.addWidget(label_cook)

        dish_label = QLabel("Выберите блюдо:")
        dish_label.setStyleSheet("font-size: 16px; color: #333;")
        cook_layout.addWidget(dish_label)

        combo_dish = QComboBox()
        combo_dish.addItems(["Блюдо 1", "Блюдо 2", "Блюдо 3"])
        combo_dish.setStyleSheet("""
            QComboBox {
                font-size: 16px;
                color: #000;
                background-color: #fff;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #fff;
                selection-background-color: #d0d0d0;
                color: #000;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        cook_layout.addWidget(combo_dish)

        qty_label = QLabel("Количество блюд:")
        qty_label.setStyleSheet("font-size: 16px; color: #333;")
        cook_layout.addWidget(qty_label)

        qty_edit = QLineEdit()
        qty_edit.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                padding: 5px;
                color: #000;
                background-color: #fff;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)
        cook_layout.addWidget(qty_edit)

        btn_layout = QHBoxLayout()
        btn_start_cook = QPushButton("Старт")
        btn_stop_cook = QPushButton("Стоп")
        for btn in (btn_start_cook, btn_stop_cook):
            btn.setFlat(True)
            btn.setStyleSheet("""
                QPushButton {
                    color: #333;
                    background-color: #e0e0e0;
                    border: 1px solid #ccc;
                    font-size: 16px;
                    padding: 5px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
                QPushButton:pressed {
                    background-color: #c0c0c0;
                }
            """)
            btn_layout.addWidget(btn)
        btn_start_cook.clicked.connect(self.startCook)
        btn_stop_cook.clicked.connect(self.stopCook)
        cook_layout.addLayout(btn_layout)

        # Добавляем страницы в переключатель
        self.stacked_widget.addWidget(self.page_anti_afk)
        self.stacked_widget.addWidget(self.page_cook)

        # Добавляем сайдбар и основную область в layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stacked_widget)

        # Связываем кнопки меню с переключением страниц
        self.btn_anti_afk.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.page_anti_afk))
        self.btn_cook.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.page_cook))

    def startAntiAFK(self):
        import os, sys, subprocess
        print("Запуск Anti AFK")
        # Формируем путь к файлу antiafk.py внутри папки modules, которая находится в src
        antiafk_path = os.path.join(os.path.dirname(__file__), "modules", "AntiAfkService", "antiafk.py")
        # Преобразуем путь в абсолютный
        antiafk_path = os.path.abspath(antiafk_path)
        # Проверяем, существует ли файл
        if not os.path.exists(antiafk_path):
            print("Файл antiafk.py не найден по пути:", antiafk_path)
            return
        # Запускаем antiafk.py с использованием интерпретатора из виртуального окружения
        self.anti_afk_process = subprocess.Popen([sys.executable, antiafk_path])
        print("Anti AFK запущен")

    def stopAntiAFK(self):
        print("Остановка Anti AFK")
        if self.anti_afk_process is not None:
            self.anti_afk_process.terminate()
            self.anti_afk_process = None
            print("Anti AFK остановлен")

    def startCook(self):
        print("Запуск Cook")
        # Здесь можно добавить вызов функционала для режима Cook,
        # например, через subprocess или импорт функции из другого модуля.
        pass

    def stopCook(self):
        print("Остановка Cook")
        # Здесь можно добавить вызов функции остановки режима Cook.
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
