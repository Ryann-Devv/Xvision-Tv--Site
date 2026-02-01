from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt, os, datetime, requests

app = Flask(__name__)
CORS(app)

# ---------------- DATABASE ----------------
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["xvision"]

customers = db["customers"]
staff = db["staff"]
pending = db["pending"]
films = db["films"]
support = db["support"]
audit = db["audit"]

# ---------------- ENV ----------------
RESEND = os.getenv("RESEND_API_KEY")
ADMIN = os.getenv("ADMIN_EMAIL")
SUBS = os.getenv("SUBSCRIPTIONS_EMAIL")

# ---------------- EMAIL ----------------
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

# ---------------- AUDIT ----------------
def log(action, actor):
    audit.insert_one({
        "action": action,
        "actor": actor,
        "time": datetime.datetime.utcnow().isoformat()
    })

# ---------------- PUBLIC ----------------
@app.route("/request/account", methods=["POST"])
def request_account():
    data = request.get_json()
    pending.insert_one(data)
    send_email(SUBS, "New Account Request", f"<p>{data['email']}</p>")
    log("Account requested", data["email"])
    return jsonify({"ok": True})

# ---------------- CUSTOMER ----------------
@app.route("/customer/login", methods=["POST"])
def customer_login():
    d = request.get_json()
    u = customers.find_one({"email": d["email"]})
    if not u or not bcrypt.checkpw(d["password"].encode(), u["password"]):
        return jsonify({"error": "Invalid"}), 401

    log("Customer login", u["email"])
    return jsonify({"email": u["email"], "expires": u["expires"]})

@app.route("/customer/film", methods=["POST"])
def customer_film():
    d = request.get_json()
    films.insert_one(d)
    log("Film request", d["email"])
    return jsonify({"ok": True})

@app.route("/customer/support", methods=["POST"])
def customer_support():
    d = request.get_json()
    support.insert_one(d)
    send_email(ADMIN, "Support Request", d["message"])
    log("Support request", d["email"])
    return jsonify({"ok": True})

# ---------------- STAFF ----------------
@app.route("/staff/login", methods=["POST"])
def staff_login():
    d = request.get_json()
    s = staff.find_one({"email": d["email"]})
    if not s or s["password"] != d["password"]:
        return jsonify({"error": "Invalid"}), 401

    log("Staff login", s["email"])
    return jsonify({"email": s["email"], "role": s.get("role","staff")})

@app.route("/staff/create", methods=["POST"])
def staff_create():
    d = request.get_json()
    customers.insert_one({
        "email": d["email"],
        "password": bcrypt.hashpw(d["password"].encode(), bcrypt.gensalt()),
        "expires": d["expires"],
        "rem14": False,
        "rem3": False
    })
    log("Customer created", d["email"])
    return jsonify({"ok": True})

@app.route("/staff/pending")
def staff_pending():
    return jsonify(list(pending.find({},{"_id":0})))

@app.route("/staff/films")
def staff_films():
    return jsonify(list(films.find({},{"_id":0})))

@app.route("/staff/support")
def staff_support():
    return jsonify(list(support.find({},{"_id":0})))

@app.route("/staff/audit")
def staff_audit():
    return jsonify(list(audit.find({},{"_id":0})))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
