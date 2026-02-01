# Add these routes to your existing app.py

@app.route("/staff/customers")
def get_customers():
    """Get all customers for admin table"""
    customers_list = list(customers.find({}, {"_id": 0, "password": 0}))
    return jsonify(customers_list)

@app.route("/staff/films")
def get_films():
    """Get all film requests"""
    films_list = list(films.find({}, {"_id": 0}))
    return jsonify(films_list)

@app.route("/staff/support-tickets")
def get_support_tickets():
    """Get all support tickets"""
    tickets = list(support.find({}, {"_id": 0}))
    return jsonify(tickets)

@app.route("/staff/delete/pending/<email>", methods=["DELETE"])
def delete_pending_request(email):
    """Delete a pending request"""
    pending.delete_one({"email": email})
    return jsonify({"ok": True})

@app.route("/staff/delete/customer/<email>", methods=["DELETE"])
def delete_customer(email):
    """Delete a customer account"""
    customers.delete_one({"email": email})
    return jsonify({"ok": True})