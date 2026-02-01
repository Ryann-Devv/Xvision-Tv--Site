from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt, os, requests

app = Flask(__name__)
CORS(app)

# ---------- DB ----------
client = MongoClient(os.getenv("MONGO_URI"))
db = client["xvision"]

customers = db.customers
pending = db.pending
staff = db.staff
films = db.films
support = db.support

# ---------- ENV ----------
RESEND = os.getenv("RESEND_API_KEY")
ADMIN = os.getenv("ADMIN_EMAIL")
SUBS = os.getenv("SUBSCRIPTIONS_EMAIL")

# ---------- EMAIL ----------
def send_email(to, subject, html):
    if not RESEND:
        return
    requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {RESEND}"},
        json={
            "from": "XVision <no-reply@xvision-tv.xyz>",
            "to": to,
            "subject": subject,
            "html": html
        }
    )

# ---------- PUBLIC ----------
@app.route("/request/account", methods=["POST"])
def request_account():
    data = request.get_json()
    pending.insert_one(data)
    send_email(SUBS, "New Account Request", data["email"])
    return jsonify({"ok": True})

# ---------- CUSTOMER ----------
@app.route("/customer/login", methods=["POST"])
def customer_login():
    d = request.get_json()
    u = customers.find_one({"email": d["email"]})

    if not u:
        return jsonify({"error": "Invalid"}), 401

    if not bcrypt.checkpw(d["password"].encode(), u["password"]):
        return jsonify({"error": "Invalid"}), 401

    return jsonify({"email": u["email"], "expires": u["expires"]})

@app.route("/request/film", methods=["POST"])
def request_film():
    films.insert_one(request.get_json())
    return jsonify({"ok": True})

@app.route("/request/support", methods=["POST"])
def request_support():
    d = request.get_json()
    support.insert_one(d)
    send_email(ADMIN, "Support Request", d["message"])
    return jsonify({"ok": True})

# ---------- STAFF ----------
@app.route("/staff/login", methods=["POST"])
def staff_login():
    d = request.get_json()
    u = staff.find_one({"email": d["email"]})

    if not u:
        return jsonify({"error": "Invalid"}), 401

    stored = u["password"].encode() if isinstance(u["password"], str) else u["password"]

    # ✅ If already hashed
    if stored.startswith(b"$2"):
        if not bcrypt.checkpw(d["password"].encode(), stored):
            return jsonify({"error": "Invalid"}), 401

    # ⚠️ Plain‑text fallback (ONE TIME)
    else:
        if d["password"] != u["password"]:
            return jsonify({"error": "Invalid"}), 401

        # Auto‑upgrade to bcrypt
        staff.update_one(
            {"email": u["email"]},
            {"$set": {
                "password": bcrypt.hashpw(d["password"].encode(), bcrypt.gensalt())
            }}
        )

    return jsonify({"email": u["email"], "role": u.get("role", "staff")})

@app.route("/staff/create", methods=["POST"])
def staff_create_customer():
    d = request.get_json()
    customers.insert_one({
        "email": d["email"],
        "password": bcrypt.hashpw(d["password"].encode(), bcrypt.gensalt()),
        "expires": d["expires"]
    })
    return jsonify({"ok": True})

@app.route("/staff/pending")
def staff_pending():
    return jsonify(list(pending.find({}, {"_id": 0})))

if __name__ == "__main__":
    app.run()
