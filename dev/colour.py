import cv2
import numpy as np
import pyautogui
import time
import tkinter as tk


def get_color_at_cursor():
    """Определяет цвет пикселя, на который указывает курсор."""
    x, y = pyautogui.position()
    screenshot = pyautogui.screenshot(region=(x, y, 1, 1))
    color = np.array(screenshot)[0, 0]  # Получаем цвет пикселя (BGR)
    return tuple(color[::-1])  # Преобразуем в RGB


def update_color():
    color = get_color_at_cursor()
    color_hex = "#{:02x}{:02x}{:02x}".format(*color)
    label.config(text=f"Цвет под курсором (RGB): {color}\nHEX: {color_hex}", bg=color_hex, fg="black" if sum(color) > 382 else "white")
    root.after(500, update_color)


# Создание окна
root = tk.Tk()
root.title("Определение цвета под курсором")
root.geometry("300x100")

label = tk.Label(root, text="", font=("Arial", 14))
label.pack(expand=True, fill="both")

update_color()
root.mainloop()