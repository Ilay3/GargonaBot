import tkinter as tk
from pynput import mouse

def update_label(x, y):
    label.config(text=f"X: {x}, Y: {y}")

def on_move(x, y):
    update_label(x, y)

# Создаем главное окно
root = tk.Tk()
root.title("Координаты курсора")
root.geometry("200x100")

label = tk.Label(root, text="X: 0, Y: 0", font=("Arial", 14))
label.pack(pady=20)

# Запускаем слушателя мыши
listener = mouse.Listener(on_move=on_move)
listener.start()

# Запускаем главный цикл Tkinter
root.mainloop()

# Останавливаем слушателя при закрытии окна
listener.stop()
