import sys
import os

def resource_path(relative_path, base_folder=""):
    """
    Возвращает абсолютный путь к файлу-ресурсу.
    Если приложение собрано через PyInstaller, используется sys._MEIPASS.
    Иначе базовый путь берётся из каталога, где расположен этот модуль (src).
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    if base_folder:
        base_path = os.path.join(base_path, base_folder)
    return os.path.join(base_path, relative_path)

def get_image_path(*path_segments):
    """
    Возвращает абсолютный путь к изображению.
    Предполагается, что все изображения лежат в папке "resources/images" (относительно src).
    Например, вызов:
        get_image_path("ImgWaxta", "ButtonE.png")
    сформирует путь: src/resources/images/ImgWaxta/ButtonE.png
    """
    base_folder = os.path.join("resources", "images")
    relative_path = os.path.join(*path_segments)
    return resource_path(relative_path, base_folder=base_folder)
