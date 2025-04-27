import sys
from pathlib import Path


def resource_path(relative_path: str | Path) -> Path:
    """
    Возвращает абсолютный путь к ресурсу, работает для dev и packaged приложения.

    :param relative_path: Относительный путь к ресурсу
    :return: Абсолютный Path объект
    """
    try:
        # PyInstaller создает временную папку в _MEIPASS
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # Базовый путь для режима разработки
        base_path = Path(__file__).parent.parent  # предполагается src как корень

    full_path = base_path / relative_path
    if not full_path.exists():
        raise FileNotFoundError(f"Resource not found: {full_path}")
    return full_path.resolve()


def get_image_path(*path_segments: str) -> Path:
    """
    Генерирует путь к изображениям в директории resources/images

    :param path_segments: Компоненты пути относительно resources/images
    :return: Абсолютный Path объект
    """
    return resource_path(Path("resources", "images", *path_segments))