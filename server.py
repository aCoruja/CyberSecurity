from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import time
import jwt

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)  # permite fetch de JS

JWT_SECRET = "supersecretkey"
JWT_ALG = "HS256"
JWT_EXP_SECONDS = 3600

# Usuário de teste
users = {
    "joao": {
        "name": "João Silva",
        "password": "1234"
    }
}

# Página inicial
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

# Endpoint de login -> devolve JWT
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    user = users.get(username)
    if not user or user["password"] != password:
        return jsonify({"error": "Usuário ou senha inválidos"}), 401

    iat = int(time.time())
    exp = iat + JWT_EXP_SECONDS
    payload = {"name": user["name"], "iat": iat, "exp": exp}

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
    return jsonify({"token": token})

# Endpoint de teste do token
@app.route("/validate-token", methods=["POST"])
def validate_token():
    data = request.get_json() or {}
    token = data.get("token")
    if not token:
        return jsonify({"error": "token required"}), 400
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return jsonify({"valid": True, "payload": decoded})
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
