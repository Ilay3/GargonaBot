import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk  # Подключаем Pillow для работы с изображениями

# Функция для кнопок "В разработке"
def show_coming_soon():
    messagebox.showinfo("В разработке", "Сделано позже")

# Функция для окна с ползунками
def open_toggle_window():
    toggle_window = tk.Toplevel(root)
    toggle_window.title("Настройки")

    toggles = {}
    toggle_labels = {}

    def toggle(name):
        state = "Вкл" if toggles[name].get() else "Выкл"
        toggle_labels[name].config(text=f"{name}: {state}")

    for i in range(3):  # Добавляем 3 ползунка (можно больше)
        name = f"Опция {i+1}"
        toggles[name] = tk.BooleanVar()
        frame = tk.Frame(toggle_window)
        frame.pack(pady=5)

        toggle_labels[name] = tk.Label(frame, text=f"{name}: Выкл", font=("Arial", 12))
        toggle_labels[name].pack(side="left")

        toggle_btn = ttk.Checkbutton(frame, variable=toggles[name], command=lambda n=name: toggle(n))
        toggle_btn.pack(side="right")

# Функция для обновления размеров логотипа и кнопок
def resize_elements(event=None):
    """Автоматически изменяет размер логотипа и кнопок при изменении размера окна."""
    window_width = root.winfo_width()
    button_size = window_width // 4  # Квадратные кнопки (четверть ширины окна)

    # Обновляем логотип
    if os.path.exists(logo_path):
        img = Image.open(logo_path)
        new_width = window_width - 50  # Отнимаем немного от ширины окна для отступов
        new_height = int((img.height / img.width) * new_width)  # Сохраняем пропорции
        img_resized = img.resize((new_width, new_height), Image.LANCZOS)
        logo_img_resized = ImageTk.PhotoImage(img_resized)
        logo_label.config(image=logo_img_resized)
        logo_label.image = logo_img_resized  # Сохраняем ссылку

    # Обновляем размеры кнопок
    for btn in buttons:
        btn.config(width=button_size, height=button_size // 4)  # Пропорция 1:4 для читабельности текста

# Создание главного окна
root = tk.Tk()
root.title("Gargonabot")
root.geometry("400x500")

# Получаем путь к директории с изображениями
image_dir = os.path.join(os.path.dirname(__file__), "imagesformenu")
logo_path = os.path.join(image_dir, "logo.png")

# Логотип
if os.path.exists(logo_path):
    img = Image.open(logo_path)
    img_resized = img.resize((200, 100), Image.LANCZOS)  # Начальный размер
    logo_img = ImageTk.PhotoImage(img_resized)

    logo_label = tk.Label(root, image=logo_img)
    logo_label.pack(pady=10)
else:
    logo_label = tk.Label(root, text="Логотип не найден", font=("Arial", 12, "bold"))
    logo_label.pack(pady=10)

# Название приложения
title_label = tk.Label(root, text="GargonaBot", font=("Arial", 16, "bold"))
title_label.pack(pady=5)

# Функциональные кнопки (список для обновления размеров)
buttons = []
for i in range(9):
    btn = tk.Button(root, text=f"Кнопка {i+1}", command=show_coming_soon)
    btn.pack(pady=5)
    buttons.append(btn)

# 10-я кнопка открывает окно с ползунками
btn_settings = tk.Button(root, text="Настройки", command=open_toggle_window)
btn_settings.pack(pady=5)
buttons.append(btn_settings)

# Привязываем изменение размеров элементов к изменению размера окна
root.bind("<Configure>", resize_elements)

# Запуск приложения
root.mainloop()
