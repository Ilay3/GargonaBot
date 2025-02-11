from flask import Flask, request, jsonify
import json
import datetime
import os

app = Flask(__name__)

DATABASE_FILE = "database.json"


# Загружаем базу данных лицензий
def load_database():
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r") as f:
            return json.load(f)
    return {}


# Сохраняем базу данных лицензий
def save_database(db):
    with open(DATABASE_FILE, "w") as f:
        json.dump(db, f, indent=4)


# Проверка и активация ключа
@app.route("/validate", methods=["POST"])
def validate_key():
    data = request.json
    key = data.get("key")
    hwid = data.get("hwid")

    db = load_database()

    if key not in db:
        return jsonify({"message": "Invalid key"}), 400

    license_data = db[key]

    # Проверяем, активирован ли ключ
    if "hwid" in license_data:
        if license_data["hwid"] != hwid:
            return jsonify({"message": "Key already activated on another device"}), 400
    else:
        # Привязываем ключ к устройству
        db[key]["hwid"] = hwid
        save_database(db)

    expiry_date = datetime.datetime.strptime(license_data["expiry_date"], "%Y-%m-%d %H:%M:%S")

    if expiry_date < datetime.datetime.now():
        return jsonify({"message": "License expired"}), 400

    return jsonify({"message": "License valid", "expiry_date": license_data["expiry_date"]}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
