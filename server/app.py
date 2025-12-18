from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import bcrypt

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:8000"}})
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
    password = data.get("password")

    if not username or not password:
        return jsonify({"status":"error","message":"Missing username or password"}), 400

    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
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

    if not username or not password:
        return jsonify({"status":"error","message":"Missing username or password"}), 400

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
        return jsonify({"status": "success", "user_id": user["id"]}), 200
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
    conn.execute( "INSERT INTO words (dictionary_id, word, translation) VALUES (?, ?, ?)", (dictionary_id, word, translation) ) 
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

@app.route("/edit_word/<int:word_id>", methods=["PUT"]) 
def edit_word(word_id): 
    data = request.json 
    word = data.get("word") 
    translation = data.get("translation")

    conn = get_db_connection() 
    conn.execute("UPDATE words SET word=?, translation=? WHERE id=?", (word, translation, word_id)) 
    conn.commit() 
    conn.close() 
    return jsonify({"status": "success"}), 200

@app.route("/delete_word/<int:word_id>", methods=["DELETE"]) 
def delete_word(word_id): 
    conn = get_db_connection() 
    conn.execute("DELETE FROM words WHERE id=?", (word_id,)) 
    conn.commit() 
    conn.close() 
    return jsonify({"status": "success"}), 200



if __name__ == "__main__":
    app.run(debug=True)
