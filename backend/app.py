from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt, os, datetime, requests

app = Flask(__name__)
CORS(app)

db = MongoClient(os.getenv("MONGO_URI"))["xvision"]

customers = db.customers
pending = db.pending
staff = db.staff
films = db.films
support = db.support

RESEND = os.getenv("RESEND_API_KEY")
ADMIN = os.getenv("ADMIN_EMAIL")
SUBS = os.getenv("SUBSCRIPTIONS_EMAIL")

# ---------- EMAIL ----------
def send_email(to, subject, html):
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
        exp = datetime.date.fromisoformat(u["expires"])
        days = (exp - today).days

        if days == 14 and not u.get("rem14"):
            send_email(u["email"], "XVision Renewal Reminder",
                       "<p>Your subscription expires in 14 days.</p>")
            customers.update_one({"email":u["email"]},{"$set":{"rem14":True}})

        if days == 3 and not u.get("rem3"):
            send_email(u["email"], "XVision Expiring Soon",
                       "<p>Your subscription expires in 3 days.</p>")
            customers.update_one({"email":u["email"]},{"$set":{"rem3":True}})

check_renewals()

# ---------- PUBLIC ----------
@app.route("/request/account", methods=["POST"])
def request_account():
    pending.insert_one(request.json)
    send_email(SUBS, "New Account Request", request.json["email"])
    return jsonify({"ok":True})

# ---------- CUSTOMER ----------
@app.route("/customer/login", methods=["POST"])
def customer_login():
    u = customers.find_one({"email":request.json["email"]})
    if u and bcrypt.checkpw(request.json["password"].encode(), u["password"]):
        return jsonify({"email":u["email"],"expires":u["expires"]})
    return jsonify({"error":"Invalid"}),401

@app.route("/request/film", methods=["POST"])
def film():
    films.insert_one(request.json)
    return jsonify({"ok":True})

@app.route("/request/support", methods=["POST"])
def support_req():
    support.insert_one(request.json)
    send_email(ADMIN, "New Support Request", request.json["message"])
    return jsonify({"ok":True})

# ---------- STAFF ----------
@app.route("/staff/login", methods=["POST"])
def staff_login():
    data = request.json
    staff = staff_col.find_one({
        "email": data["email"],
        "password": data["password"]
    })

    if not staff:
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({
        "email": staff["email"],
        "role": staff.get("role", "staff")
    })


@app.route("/staff/create", methods=["POST"])
def create_customer():
    d = request.json
    customers.insert_one({
        "email": d["email"],
        "password": bcrypt.hashpw(d["password"].encode(), bcrypt.gensalt()),
        "expires": d["expires"],
        "rem14": False,
        "rem3": False
    })
    return jsonify({"ok":True})

@app.route("/staff/pending")
def staff_pending():
    return jsonify(list(pending.find({},{"_id":0})))

if __name__ == "__main__":
    app.run()
