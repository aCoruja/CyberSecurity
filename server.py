from flask import Flask, request, jsonify, render_template
from werkzeug.security import check_password_hash
import time
import jwt

# ------------------ CONFIG ------------------
app = Flask(__name__, template_folder='templates', static_folder='static')

JWT_SECRET = "supersecretkey"       # coloque uma chave segura
JWT_ALG = "HS256"
JWT_EXP_SECONDS = 3600               # 1 hora

# Simulação de usuários (exemplo)
users = {
    "joao.silva": {
        "sub": "1234567890",
        "name": "Joao Silva",
        "email": "joao.silva@example.com",
        "role": "admin",
        "password_hash": "pbkdf2:sha256:150000$example$e5a..."  # hash de exemplo
    }
}

# Simulação de clients
clients = {
    "example-client-1": {
        "name": "App Exemplo",
        "clientSecret": "secret123",
        "redirect_uri": "https://example.com/callback"
    }
}

# ------------------ ROTAS ------------------

# Página inicial
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

# Endpoint de validação do client
@app.route("/auth", methods=["POST"])
def auth_client():
    data = request.get_json() or {}
    client_id = data.get("clientID")
    client_secret = data.get("clientSecret")

    client = clients.get(client_id)
    if client and client.get("clientSecret") == client_secret:
        return jsonify({"status": "client_valid"}), 200

    return jsonify({"error": "clientID ou clientSecret inválidos"}), 401

# Endpoint de login de usuário -> devolve JWT
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Preencha username e senha"}), 400

    user = users.get(username)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Usuário ou senha inválidos"}), 401

    iat = int(time.time())
    exp = iat + JWT_EXP_SECONDS

    payload = {
        "sub": user.get("sub", "1234567890"),
        "name": user.get("name", username),
        "email": user.get("email", ""),
        "role": user.get("role", "user"),
        "iat": iat,
        "exp": exp
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

    return jsonify({"token": token})

# Endpoint de validação de token
@app.route("/validate-token", methods=["POST"])
def validate_token():
    data = request.get_json() or {}
    token = data.get("token")
    if not token:
        return jsonify({"error": "token required"}), 400
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return jsonify({"valid": True, "payload": decoded})
    except jwt.ExpiredSignatureError:
        return jsonify({"valid": False, "error": "token expired"}), 401
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 401

# ------------------ RUN ------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
