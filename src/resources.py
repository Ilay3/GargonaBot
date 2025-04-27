import sys
from pathlib import Path

def resource_path(relative_path: str | Path) -> Path:
    """
    Фиктивная функция для совместимости со старым кодом.
    В новой архитектуре не используется, оставлена для обратной совместимости.
    """
    return Path(relative_path)

def get_image_path(*path_segments: str) -> str:
    """Возвращает виртуальный путь к изображению для работы с ImageLoader"""
    return str(Path(*path_segments))