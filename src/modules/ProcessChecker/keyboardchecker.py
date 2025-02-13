import ctypes
import tkinter as tk
from tkinter import messagebox

# Определение языковых идентификаторов
LANG_RUSSIAN = 0x0419  # Русская раскладка
LANG_ENGLISH = 0x0409  # Английская раскладка

def get_keyboard_layout():
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    hwnd = user32.GetForegroundWindow()
    thread_id = user32.GetWindowThreadProcessId(hwnd, None)
    layout_id = user32.GetKeyboardLayout(thread_id)
    return layout_id & 0xFFFF

def check_layout():
    if get_keyboard_layout() == LANG_RUSSIAN:
        messagebox.showwarning("Внимание!", "Пожалуйста, переключите раскладку клавиатуры на английскую, наш бот работает только с ней!")
    root.after(10000, check_layout)  # Запуск через 10 секунд

root = tk.Tk()
root.withdraw()  # Скрыть основное окно
check_layout()
root.mainloop()
