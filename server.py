from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import time
import jwt

app = Flask(__name__)

JWT_SECRET = "MEUSEGREDO"
JWT_ALG = "HS256"
JWT_EXP_SECONDS = 3600

# ---- CLIENTES ----
clients = {
    "example-client-1": {
        "name": "App Exemplo",
        "clientSecret": "secret123",
        "redirect_uri": "https://example.com/callback"
    }
}

# ---- USUÁRIOS ----
users = {}  # {username: {...}}

# ---- PRODUTOS ----
products = [
    {"id": 1, "name": "Teclado Mecânico", "price": 199, "img": ""},
    {"id": 2, "name": "Mouse Gamer", "price": 129, "img": ""},
    {"id": 3, "name": "Headset RGB", "price": 249, "img": ""}
]

# ---- CARRINHOS ----
carts = {}  # {username: [{product_id, qty}]}


def create_token(user):
    now = int(time.time())
    payload = {
        "sub": user["username"],
        "name": user["username"],
        "email": user["email"],
        "iat": now,
        "exp": now + JWT_EXP_SECONDS
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def get_user_from_token(request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None

    token = auth.split(" ")[1]

    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        username = decoded["sub"]
        return users.get(username)
    except:
        return None


# ==========================
#      ROTAS DA API
# ==========================

@app.route("/auth", methods=["POST"])
def auth_client():
    data = request.get_json()
    clientID = data.get("clientID")
    clientSecret = data.get("clientSecret")

    client = clients.get(clientID)

    if not client or client["clientSecret"] != clientSecret:
        return jsonify({"error": "clientID ou clientSecret inválidos"}), 401

    return jsonify({"message": "client validado"})


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if username in users:
        return jsonify({"error": "usuário já existe"}), 400

    users[username] = {
        "username": username,
        "email": email,
        "password_hash": generate_password_hash(password)
    }

    return jsonify({"message": "registrado"})


@app.route("/login", methods=["POST"])
def login_json():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = users.get(username)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "credenciais inválidas"}), 401

    token = create_token(user)
    return jsonify({"token": token})


@app.route("/products", methods=["GET"])
def get_products():
    return jsonify(products)


@app.route("/cart", methods=["GET", "POST", "PUT", "DELETE"])
def cart_ops():
    user = get_user_from_token(request)
    if not user:
        return jsonify({"error": "unauthorized"}), 401

    username = user["username"]
    if username not in carts:
        carts[username] = []

    # GET → retornar
    if request.method == "GET":
        return jsonify({"cart": carts[username]})

    data = request.get_json()

    # POST → adicionar item
    if request.method == "POST":
        carts[username].append({
            "product_id": data["product_id"],
            "qty": data.get("qty", 1)
        })
        return jsonify({"cart": carts[username]})

    # PUT → substituir lista
    if request.method == "PUT":
        carts[username] = data.get("items", [])
        return jsonify({"cart": carts[username]})

    # DELETE → limpar
    if request.method == "DELETE":
        carts[username] = []
        return jsonify({"cart": []})


@app.route("/checkout", methods=["POST"])
def checkout():
    user = get_user_from_token(request)
    if not user:
        return jsonify({"error": "unauthorized"}), 401

    username = user["username"]
    order_id = int(time.time())

    # limpar carrinho
    carts[username] = []

    return jsonify({
        "order": {"id": order_id},
        "message": "pedido concluído"
    })


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "API online"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)
