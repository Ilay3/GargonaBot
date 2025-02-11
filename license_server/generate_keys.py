import json
import datetime
import uuid

DATABASE_FILE = "database.json"

# Генерация уникального ключа
def generate_key(days):
    return f"{days}DAY-" + str(uuid.uuid4()).split("-")[0].upper()

# Добавление ключа в базу данных
def add_key(days):
    db = {}
    if days not in [3, 14, 30]:
        print("Неверный срок подписки")
        return

    if database_exists():
        db = load_database()

    key = generate_key(days)
    expiry_date = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

    db[key] = {
        "expiry_date": expiry_date,
        "hwid": None
    }

    save_database(db)
    print(f"Сгенерирован ключ: {key} (Действителен до {expiry_date})")

def database_exists():
    try:
        with open(DATABASE_FILE, "r") as f:
            return True
    except FileNotFoundError:
        return False

def load_database():
    with open(DATABASE_FILE, "r") as f:
        return json.load(f)

def save_database(db):
    with open(DATABASE_FILE, "w") as f:
        json.dump(db, f, indent=4)

if __name__ == "__main__":
    days = int(input("Введите срок подписки (3, 14, 30 дней): "))
    add_key(days)
