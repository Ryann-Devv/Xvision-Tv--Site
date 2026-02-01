from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt, os, requests
from datetime import datetime

# === MUST BE FIRST ===
app = Flask(__name__)
CORS(app)

# ---------- DB WITH ERROR HANDLING ----------
try:
    # Get MongoDB URI from environment variable
    MONGO_URI = os.getenv("MONGO_URI")
    if not MONGO_URI:
        print("⚠️  MONGO_URI environment variable not set")
        raise ValueError("MONGO_URI not configured")
    
    # Connect to MongoDB Atlas cluster
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    
    # Test connection
    client.server_info()
    print("✅ Connected to MongoDB Atlas")
    
    db = client["xvision"]  # Database name
    
    # Collections
    customers = db.customers
    pending = db.pending
    staff = db.staff
    films = db.films
    support = db.support
    
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")
    print("⚠️  Running in fallback mode - database operations will fail")
    # Create None placeholders
    customers = pending = staff = films = support = None

# ---------- ENV ----------
RESEND = os.getenv("RESEND_API_KEY")
ADMIN = os.getenv("ADMIN_EMAIL")
SUBS = os.getenv("SUBSCRIPTIONS_EMAIL")

# ---------- EMAIL ----------
def send_email(to, subject, html):
    if not RESEND:
        print(f"📧 [SIMULATED] Email to {to}: {subject}")
        return True
    
    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND}"},
            json={
                "from": "XVision <no-reply@xvision-tv.xyz>",
                "to": to,
                "subject": subject,
                "html": html
            },
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False

# ---------- PUBLIC ----------
@app.route("/request/account", methods=["POST"])
def request_account():
    try:
        data = request.get_json()
        if not data or "email" not in data:
            return jsonify({"error": "Email required"}), 400
        
        if pending is None:
            return jsonify({"error": "Database unavailable"}), 503
        
        # Add timestamp
        data["date"] = datetime.now().isoformat()
        pending.insert_one(data)
        
        send_email(SUBS, "New Account Request", 
                  f"<p>New account request from: {data['email']}</p>")
        
        return jsonify({"ok": True, "message": "Request submitted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- CUSTOMER ----------
@app.route("/customer/login", methods=["POST"])
def customer_login():
    try:
        d = request.get_json()
        if not d or "email" not in d or "password" not in d:
            return jsonify({"error": "Email and password required"}), 400
        
        if customers is None:
            return jsonify({"error": "Database unavailable"}), 503
        
        u = customers.find_one({"email": d["email"]})
        
        if not u:
            return jsonify({"error": "Invalid credentials"}), 401
        
        if not bcrypt.checkpw(d["password"].encode(), u["password"]):
            return jsonify({"error": "Invalid credentials"}), 401
        
        return jsonify({
            "email": u["email"], 
            "expires": u.get("expires", "2025-12-31")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/request/film", methods=["POST"])
def request_film():
    try:
        data = request.get_json()
        if not data or "title" not in data:
            return jsonify({"error": "Film title required"}), 400
        
        if films is None:
            return jsonify({"error": "Database unavailable"}), 503
        
        data["date"] = datetime.now().isoformat()
        films.insert_one(data)
        
        return jsonify({"ok": True, "message": "Film request submitted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/request/support", methods=["POST"])
def request_support():
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Message required"}), 400
        
        if support is None:
            return jsonify({"error": "Database unavailable"}), 503
        
        data["date"] = datetime.now().isoformat()
        data["status"] = "open"
        support.insert_one(data)
        
        send_email(ADMIN, "Support Request", 
                  f"<p>Message: {data['message']}</p>")
        
        return jsonify({"ok": True, "message": "Support request submitted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- STAFF ----------
@app.route("/staff/login", methods=["POST"])
def staff_login():
    try:
        d = request.get_json()
        if not d or "email" not in d or "password" not in d:
            return jsonify({"error": "Email and password required"}), 400
        
        if staff is None:
            return jsonify({"error": "Database unavailable"}), 503
        
        u = staff.find_one({"email": d["email"]})
        
        if not u:
            return jsonify({"error": "Invalid credentials"}), 401
        
        stored = u["password"]
        
        # Handle different password formats
        if isinstance(stored, bytes) and stored.startswith(b"$2"):
            # Bcrypt bytes
            if not bcrypt.checkpw(d["password"].encode(), stored):
                return jsonify({"error": "Invalid credentials"}), 401
        elif isinstance(stored, str) and stored.startswith("$2"):
            # Bcrypt string
            if not bcrypt.checkpw(d["password"].encode(), stored.encode()):
                return jsonify({"error": "Invalid credentials"}), 401
        else:
            # Plain-text fallback (ONE TIME)
            plain_text = stored if isinstance(stored, str) else stored.decode('utf-8', 'ignore')
            if d["password"] != plain_text:
                return jsonify({"error": "Invalid credentials"}), 401
            
            # Auto-upgrade to bcrypt
            new_hash = bcrypt.hashpw(d["password"].encode(), bcrypt.gensalt())
            staff.update_one(
                {"email": u["email"]},
                {"$set": {"password": new_hash}}
            )
        
        return jsonify({
            "email": u["email"], 
            "role": u.get("role", "staff")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/staff/create", methods=["POST"])
def staff_create_customer():
    try:
        d = request.get_json()
        required = ["email", "password", "expires"]
        for field in required:
            if field not in d:
                return jsonify({"error": f"Missing {field}"}), 400
        
        if customers is None:
            return jsonify({"error": "Database unavailable"}), 503
        
        # Check if customer already exists
        existing = customers.find_one({"email": d["email"]})
        if existing:
            return jsonify({"error": "Customer already exists"}), 409
        
        # Hash password
        hashed = bcrypt.hashpw(d["password"].encode(), bcrypt.gensalt())
        
        customers.insert_one({
            "email": d["email"],
            "password": hashed,
            "expires": d["expires"],
            "created": datetime.now().isoformat()
        })
        
        return jsonify({"ok": True, "message": "Customer created"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/staff/pending")
def staff_pending():
    try:
        if pending is None:
            return jsonify({"error": "Database unavailable"}), 503
        
        results = list(pending.find({}, {"_id": 0}).sort("date", -1))
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === NEW ADMIN ENDPOINTS FOR TABLES ===
@app.route("/staff/customers")
def get_customers():
    try:
        if customers is None:
            return jsonify({"error": "Database unavailable"}), 503
        
        customers_list = list(customers.find({}, {"_id": 0, "password": 0}).sort("created", -1))
        return jsonify(customers_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/staff/films")
def get_films():
    try:
        if films is None:
            return jsonify({"error": "Database unavailable"}), 503
        
        films_list = list(films.find({}, {"_id": 0}).sort("date", -1))
        return jsonify(films_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/staff/support-tickets")
def get_support_tickets():
    try:
        if support is None:
            return jsonify({"error": "Database unavailable"}), 503
        
        tickets = list(support.find({}, {"_id": 0}).sort("date", -1))
        return jsonify(tickets)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/staff/delete/pending/<email>", methods=["DELETE"])
def delete_pending_request(email):
    try:
        if pending is None:
            return jsonify({"error": "Database unavailable"}), 503
        
        pending.delete_one({"email": email})
        return jsonify({"ok": True, "message": "Pending request deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/staff/delete/customer/<email>", methods=["DELETE"])
def delete_customer(email):
    try:
        if customers is None:
            return jsonify({"error": "Database unavailable"}), 503
        
        customers.delete_one({"email": email})
        return jsonify({"ok": True, "message": "Customer deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/staff/delete/film/<title>", methods=["DELETE"])
def delete_film(title):
    try:
        if films is None:
            return jsonify({"error": "Database unavailable"}), 503
        
        # Note: Using title as identifier, you might want to use ID instead
        films.delete_one({"title": title})
        return jsonify({"ok": True, "message": "Film request deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/staff/delete/support/<email>", methods=["DELETE"])
def delete_support(email):
    try:
        if support is None:
            return jsonify({"error": "Database unavailable"}), 503
        
        support.delete_one({"email": email})
        return jsonify({"ok": True, "message": "Support ticket deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === HEALTH CHECK ===
@app.route("/health")
def health():
    db_status = "connected" if customers is not None else "disconnected"
    return jsonify({
        "status": "ok", 
        "time": datetime.now().isoformat(),
        "database": db_status
    })

# === START SERVER ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"
    print(f"🚀 Starting XVision backend on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
    
# Add these endpoints AFTER the existing staff endpoints but BEFORE the health check

# === STATISTICS ENDPOINTS ===
@app.route("/staff/stats")
def get_stats():
    """Get counts for all collections"""
    try:
        if any([customers is None, pending is None, films is None, support is None]):
            return jsonify({"error": "Database unavailable"}), 503
        
        stats = {
            "customers": customers.count_documents({}),
            "pending": pending.count_documents({}),
            "films": films.count_documents({}),
            "support": support.count_documents({})
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === COMPLETE TABLE ENDPOINTS ===
@app.route("/staff/films/all")
def get_all_films():
    """Get all film requests"""
    try:
        if films is None:
            return jsonify({"error": "Database unavailable"}), 503
        
        films_list = list(films.find({}, {"_id": 0}).sort("date", -1))
        return jsonify(films_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/staff/support/all")
def get_all_support():
    """Get all support tickets"""
    try:
        if support is None:
            return jsonify({"error": "Database unavailable"}), 503
        
        tickets = list(support.find({}, {"_id": 0}).sort("date", -1))
        return jsonify(tickets)
    except Exception as e:
        return jsonify({"error": str(e)}), 500