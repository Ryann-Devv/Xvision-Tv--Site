// Base URL - KEPT SAME as your current setup
const API_BASE = "https://xvision-backend-ao7z.onrender.com";

// ===== ADDED MISSING CUSTOMER FUNCTIONS =====
async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    if (!email || !password) {
        alert("Enter email and password");
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/customer/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.error || "Login failed");
            return;
        }

        // Show portal
        document.getElementById("loginBox").style.display = "none";
        document.getElementById("portal").style.display = "block";
        document.getElementById("exp").textContent = data.expires;
        
    } catch (err) {
        alert("Server error");
    }
}

async function filmReq() {
    const title = document.getElementById("film").value;
    
    if (!title) {
        alert("Enter film title");
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/request/film`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title: title })
        });

        if (res.ok) {
            alert("Film request sent");
            document.getElementById("film").value = "";
        } else {
            alert("Error");
        }
    } catch (err) {
        alert("Server error");
    }
}

async function supportReq() {
    const message = document.getElementById("msg").value;
    
    if (!message) {
        alert("Enter message");
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/request/support`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message })
        });

        if (res.ok) {
            alert("Support request sent");
            document.getElementById("msg").value = "";
        } else {
            alert("Error");
        }
    } catch (err) {
        alert("Server error");
    }
}

// ===== EXISTING FUNCTIONS (KEPT SAME) =====
async function req() {
    const email = document.getElementById("email").value;
    
    if (!email) {
        alert("Enter email");
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/request/account`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: email })
        });

        if (res.ok) {
            alert("Request sent");
        } else {
            alert("Error");
        }
    } catch (err) {
        alert("Server error");
    }
}

async function staffLogin() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    if (!email || !password) {
        alert("Missing email or password");
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/staff/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.error || "Login failed");
            return;
        }

        document.getElementById("staffLoginBox").style.display = "none";
        document.getElementById("staffPanel").style.display = "block";

    } catch (err) {
        alert("Server error");
    }
}

async function createCustomer() {
    const email = document.getElementById("cemail").value;
    const password = document.getElementById("cpass").value;
    const expires = document.getElementById("cexp").value;

    if (!email || !password || !expires) {
        alert("Missing fields");
        return;
    }

    const res = await fetch(`${API_BASE}/staff/create`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, expires })
    });

    if (res.ok) {
        alert("Customer created");
    } else {
        alert("Error creating customer");
    }
}

// ========== CUSTOMER LOGIN ==========
async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    if (!email || !password) {
        alert("Please enter email and password");
        return;
    }

    try {
        const res = await fetch("https://xvision-backend-ao7z.onrender.com/customer/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.error || "Login failed");
            return;
        }

        // Success - show customer portal
        document.getElementById("loginBox").style.display = "none";
        document.getElementById("portal").style.display = "block";
        document.getElementById("exp").textContent = data.expires;
        
        // Store user data
        localStorage.setItem("customerEmail", data.email);
        
    } catch (err) {
        alert("Server error. Please try again.");
        console.error(err);
    }
}

// ========== CUSTOMER FILM REQUEST ==========
async function filmReq() {
    const title = document.getElementById("film").value;
    const email = localStorage.getItem("customerEmail");

    if (!title) {
        alert("Please enter a film title");
        return;
    }

    try {
        const res = await fetch("https://xvision-backend-ao7z.onrender.com/request/film", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                title: title,
                email: email || "unknown",
                date: new Date().toISOString()
            })
        });

        if (res.ok) {
            alert("Film request submitted!");
            document.getElementById("film").value = "";
        } else {
            const data = await res.json();
            alert(data.error || "Failed to submit request");
        }
    } catch (err) {
        alert("Server error");
        console.error(err);
    }
}

// ========== CUSTOMER SUPPORT REQUEST ==========
async function supportReq() {
    const message = document.getElementById("msg").value;
    const email = localStorage.getItem("customerEmail") || prompt("Please enter your email:");

    if (!message) {
        alert("Please enter a message");
        return;
    }

    if (!email) {
        alert("Email is required for support");
        return;
    }

    try {
        const res = await fetch("https://xvision-backend-ao7z.onrender.com/request/support", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                email: email,
                message: message,
                date: new Date().toISOString()
            })
        });

        if (res.ok) {
            alert("Support request submitted!");
            document.getElementById("msg").value = "";
        } else {
            const data = await res.json();
            alert(data.error || "Failed to submit request");
        }
    } catch (err) {
        alert("Server error");
        console.error(err);
    }
}

// Update the success part of your login() function:
if (!res.ok) {
    alert(data.error || "Login failed");
    return;
}

// Success - show customer portal
document.getElementById("loginBox").style.display = "none";
document.getElementById("portal").style.display = "block";
document.getElementById("exp").textContent = data.expires;

// Store user data
localStorage.setItem("customerEmail", data.email);

// Update account info display
if (typeof updateAccountInfo === 'function') {
    updateAccountInfo(data.email);
}