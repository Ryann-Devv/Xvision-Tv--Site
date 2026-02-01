from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt, os, requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ---------- DB ----------
# KEPT SAME: Environment variable location unchanged
client = MongoClient(os.getenv("MONGO_URI"))
db = client["xvision"]

customers = db.customers
pending = db.pending
staff = db.staff
films = db.films
support = db.support

# ---------- ENV ----------
# KEPT SAME: Environment variable locations unchanged
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
    
    # FIXED: Added missing input check
    if not d or "email" not in d or "password" not in d:
        return jsonify({"error": "Email and password required"}), 400
    
    u = customers.find_one({"email": d["email"]})

    if not u:
        return jsonify({"error": "Invalid"}), 401

    if not bcrypt.checkpw(d["password"].encode(), u["password"]):
        return jsonify({"error": "Invalid"}), 401

    return jsonify({"email": u["email"], "expires": u["expires"]})

@app.route("/request/film", methods=["POST"])
def request_film():
    data = request.get_json()
    
    # FIXED: Added required field check
    if not data or "title" not in data:
        return jsonify({"error": "Film title required"}), 400
        
    films.insert_one(data)
    return jsonify({"ok": True})

@app.route("/request/support", methods=["POST"])
def request_support():
    d = request.get_json()
    
    # FIXED: Added required field check
    if not d or "message" not in d:
        return jsonify({"error": "Message required"}), 400
        
    support.insert_one(d)
    send_email(ADMIN, "Support Request", d["message"])
    return jsonify({"ok": True})

# ---------- STAFF ----------
@app.route("/staff/login", methods=["POST"])
def staff_login():
    d = request.get_json()
    
    # FIXED: Added missing input check
    if not d or "email" not in d or "password" not in d:
        return jsonify({"error": "Email and password required"}), 400
    
    u = staff.find_one({"email": d["email"]})

    if not u:
        return jsonify({"error": "Invalid"}), 401

    stored = u["password"]
    
    # KEPT SAME: Plain-text fallback preserved
    if isinstance(stored, bytes) and stored.startswith(b"$2"):
        # Already bcrypt bytes
        if not bcrypt.checkpw(d["password"].encode(), stored):
            return jsonify({"error": "Invalid"}), 401
    elif isinstance(stored, str) and stored.startswith("$2"):
        # Bcrypt string
        if not bcrypt.checkpw(d["password"].encode(), stored.encode()):
            return jsonify({"error": "Invalid"}), 401
    else:
        # Plain-text fallback (ONE TIME) - KEPT SAME
        plain_text = stored if isinstance(stored, str) else stored.decode('utf-8', 'ignore')
        if d["password"] != plain_text:
            return jsonify({"error": "Invalid"}), 401
        
        # Auto-upgrade to bcrypt
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
    
    # FIXED: Added missing input check
    if not d or "email" not in d or "password" not in d or "expires" not in d:
        return jsonify({"error": "All fields required"}), 400
        
    customers.insert_one({
        "email": d["email"],
        "password": bcrypt.hashpw(d["password"].encode(), bcrypt.gensalt()),
        "expires": d["expires"]
    })
    return jsonify({"ok": True})

@app.route("/staff/pending")
def staff_pending():
    return jsonify(list(pending.find({}, {"_id": 0})))

# FIXED: Added missing imports for render deployment
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)