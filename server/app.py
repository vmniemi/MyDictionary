from flask import Flask, request, jsonify

app = Flask(__name__)

users = {}
dictionaries = {}

@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")

    if not username:
        return {"error": "Username required"}, 400

    if username in users:
        return {"error": "User already exists"}, 400

    users[username] = {"dictionaries": []}
    return {"message": "User created"}, 201

@app.route("/dictionary", methods=["POST"])
def create_dictionary():
    data = request.json
    username = data.get("username")
    language = data.get("language")

    if username not in users:
        return {"error": "User not found"}, 404

    dictionary = {
        "language": language,
        "words": {}
    }

    users[username]["dictionaries"].append(dictionary)
    return {"message": "Dictionary created"}, 201

@app.route("/word", methods=["POST"])
def add_word():
    data = request.json
    username = data.get("username")
    dict_index = data.get("dict_index")
    word = data.get("word")
    translation = data.get("translation")

    try:
        dictionary = users[username]["dictionaries"][dict_index]
    except (KeyError, IndexError):
        return {"error": "Dictionary not found"}, 404

    dictionary["words"][word] = translation
    return {"message": "Word added"}, 201

if __name__ == "__main__":
    app.run(debug=True)
