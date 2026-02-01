from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt, os, datetime, requests

app = Flask(__name__)
CORS(app)

# ---------- DATABASE ----------
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)

db = client["xvision"]

customers = db["customers"]
pending = db["pending"]
staff_col = db["staff"]
films = db["films"]
support_col = db["support"]

# ---------- ENV ----------
RESEND = os.getenv("RESEND_API_KEY")
ADMIN = os.getenv("ADMIN_EMAIL")
SUBS = os.getenv("SUBSCRIPTIONS_EMAIL")

# ---------- EMAIL ----------
def send_email(to, subject, html):
    if not RESEND:
        print("RESEND API KEY MISSING")
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

# ---------- RENEWAL REMINDERS ----------
def check_renewals():
    today = datetime.date.today()

    for u in customers.find():
        try:
            exp = datetime.date.fromisoformat(u["expires"])
        except Exception:
            continue

        days = (exp - today).days

        if days == 14 and not u.get("rem14"):
            send_email(
                u["email"],
                "XVision Renewal Reminder",
                "<p>Your subscription expires in 14 days.</p>"
            )
            customers.update_one(
                {"email": u["email"]},
                {"$set": {"rem14": True}}
            )

        if days == 3 and not u.get("rem3"):
            send_email(
                u["email"],
                "XVision Expiring Soon",
                "<p>Your subscription expires in 3 days.</p>"
            )
            customers.update_one(
                {"email": u["email"]},
                {"$set": {"rem3": True}}
            )

# Run once on startup
check_renewals()

# ---------- PUBLIC ----------
@app.route("/request/account", methods=["POST"])
def request_account():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data"}), 400

    pending.insert_one(data)
    send_email(SUBS, "New Account Request", data.get("email", "No email"))

    return jsonify({"ok": True})

# ---------- CUSTOMER ----------
@app.route("/customer/login", methods=["POST"])
def customer_login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data"}), 400

    user = customers.find_one({"email": data.get("email")})

    if not user:
        return jsonify({"error": "Invalid"}), 401

    if not bcrypt.checkpw(
        data.get("password", "").encode(),
        user["password"]
    ):
        return jsonify({"error": "Invalid"}), 401

    return jsonify({
        "email": user["email"],
        "expires": user["expires"]
    })

@app.route("/request/film", methods=["POST"])
def film_request():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400

    films.insert_one(data)
    return jsonify({"ok": True})

@app.route("/request/support", methods=["POST"])
def support_request():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400

    support_col.insert_one(data)
    send_email(ADMIN, "New Support Request", data.get("message", ""))

    return jsonify({"ok": True})

# ---------- STAFF ----------
@app.route("/staff/login", methods=["POST"])
def staff_login():
    try:
        data = request.get_json(force=True)
        print("STAFF LOGIN DATA:", data)

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Missing credentials"}), 400

        staff = staff_col.find_one({"email": email})

        if not staff:
            return jsonify({"error": "Staff not found"}), 401

        if staff["password"] != password:
            return jsonify({"error": "Invalid password"}), 401

        return jsonify({
            "email": staff["email"],
            "role": staff.get("role", "staff")
        })

    except Exception as e:
        print("STAFF LOGIN ERROR:", str(e))
        return jsonify({"error": "Server error"}), 500

@app.route("/staff/create", methods=["POST"])
def create_customer():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data"}), 400

    customers.insert_one({
        "email": data["email"],
        "password": bcrypt.hashpw(
            data["password"].encode(),
            bcrypt.gensalt()
        ),
        "expires": data["expires"],
        "rem14": False,
        "rem3": False
    })

    return jsonify({"ok": True})

@app.route("/staff/pending")
def staff_pending():
    return jsonify(list(pending.find({}, {"_id": 0})))

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
