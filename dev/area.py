import pyautogui

# Разрешение экрана Full HD
screen_width = 1920
screen_height = 1080

# Размеры области (например, квадрат 500x500 или прямоугольник 800x600)
area_width = 20
area_height = 20

# Вычисление координат верхнего левого угла области
center_x = screen_width // 2
center_y = screen_height // 2

# Корректируем координаты верхнего левого угла, чтобы область была в центре
top_left_x = center_x - (area_width // 2)
top_left_y = center_y - (area_height // 2)

# Вывод координат
print(f"Координаты верхнего левого угла области: ({top_left_x}, {top_left_y})")
print(f"Координаты нижнего правого угла области: ({top_left_x + area_width}, {top_left_y + area_height})")
