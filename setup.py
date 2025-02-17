import sys
import os
from cx_Freeze import setup, Executable

# Если хотите собрать одним EXE, лучше использовать PyInstaller.
# Но если вы хотите попробовать cx_Freeze, пример:
include_files = [
    ("license.dat", "license.dat"),
    ("settings.json", "settings.json"),
    ("logs", "logs"),
    ("resources", "resources"),
    ("src\\modules", "modules"),
]

build_exe_options = {
    "packages": ["os", "sys", "json", "datetime", "subprocess", "ctypes", "uuid", "platform", "threading", "requests", "psutil", "win32gui"],
    "include_files": include_files,
    "zip_exclude_packages": [],  # Можно попробовать отключить упаковку в zip, но в нашем случае лучше использовать PyInstaller.
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="GargonaBot",
    version="1.0",
    description="Менеджер сервисов бота",
    options={"build_exe": build_exe_options},
    executables=[Executable("src/main.py", base=base)]
)
