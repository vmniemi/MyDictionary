from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DATABASE = "database.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dictionaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            language TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dictionary_id INTEGER NOT NULL,
            word TEXT NOT NULL,
            translation TEXT,
            FOREIGN KEY(dictionary_id) REFERENCES dictionaries(id)
        )
    """)
    conn.commit()
    conn.close()

init_db()



@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")  # In production: hash passwords

    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return jsonify({"status": "success"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Username exists"}), 400
    finally:
        conn.close()

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
    conn.close()

    if user:
        return jsonify({"status": "success", "user_id": user["id"]})
    else:
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@app.route("/create_dictionary", methods=["POST"])
def create_dictionary():
    data = request.json
    user_id = data.get("user_id")
    language = data.get("language")

    conn = get_db_connection()
    conn.execute("INSERT INTO dictionaries (user_id, language) VALUES (?, ?)", (user_id, language))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 201

@app.route("/add_word", methods=["POST"])
def add_word():
    data = request.json
    dictionary_id = data.get("dictionary_id")
    word = data.get("word")
    translation = data.get("translation")

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO words (dictionary_id, word, translation) VALUES (?, ?, ?)",
        (dictionary_id, word, translation)
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 201

@app.route("/get_dictionaries/<int:user_id>")
def get_dictionaries(user_id):
    conn = get_db_connection()
    dictionaries = conn.execute("SELECT * FROM dictionaries WHERE user_id=?", (user_id,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in dictionaries])

@app.route("/get_words/<int:dictionary_id>")
def get_words(dictionary_id):
    conn = get_db_connection()
    words = conn.execute("SELECT * FROM words WHERE dictionary_id=?", (dictionary_id,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in words])

if __name__ == "__main__":
    app.run(debug=True)
