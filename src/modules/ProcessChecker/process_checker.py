import psutil
import win32gui
import win32process

def is_game_active():
    """
    Проверяет, активна ли игра.
    Игра считается активной, если активное (foreground) окно принадлежит процессу с именем GTA5.exe
    или RAGE Multiplayer.exe и окно не свернуто.
    """
    game_names = ["GTA5.exe", "RAGE Multiplayer.exe"]
    hwnd = win32gui.GetForegroundWindow()
    if hwnd == 0:
        return False
    # Если окно свернуто, функция IsIconic вернет True.
    if win32gui.IsIconic(hwnd):
        return False
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        proc = psutil.Process(pid)
        if proc.name() in game_names:
            return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False
    return False
