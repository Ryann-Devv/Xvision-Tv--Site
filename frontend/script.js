// ========== CUSTOMER FUNCTIONS ==========
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
        
        // Update account info if function exists
        if (typeof updateAccountInfo === 'function') {
            updateAccountInfo(data.email);
        }
        
    } catch (err) {
        alert("Server error. Please try again.");
        console.error(err);
    }
}

async function filmReq() {
    const title = document.getElementById("film").value;
    const email = localStorage.getItem("customerEmail");
    const notes = document.getElementById("filmNotes") ? document.getElementById("filmNotes").value : "";

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
                notes: notes,
                date: new Date().toISOString()
            })
        });

        if (res.ok) {
            alert("✓ Film request submitted!");
            document.getElementById("film").value = "";
            if (document.getElementById("filmNotes")) {
                document.getElementById("filmNotes").value = "";
            }
        } else {
            const data = await res.json();
            alert("✗ " + (data.error || "Failed to submit request"));
        }
    } catch (err) {
        alert("✗ Server error. Please try again.");
        console.error(err);
    }
}

async function supportReq() {
    const message = document.getElementById("msg").value;
    const email = document.getElementById("supportEmail") ? document.getElementById("supportEmail").value : localStorage.getItem("customerEmail");
    const priority = document.getElementById("priority") ? document.getElementById("priority").value : "normal";

    if (!message) {
        alert("Please enter a message");
        return;
    }

    if (!email) {
        const userEmail = prompt("Please enter your email:");
        if (!userEmail) {
            alert("Email is required for support");
            return;
        }
        if (document.getElementById("supportEmail")) {
            document.getElementById("supportEmail").value = userEmail;
        }
    }

    try {
        const res = await fetch("https://xvision-backend-ao7z.onrender.com/request/support", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                email: email,
                message: message,
                priority: priority,
                date: new Date().toISOString()
            })
        });

        if (res.ok) {
            alert("✓ Support request submitted!");
            document.getElementById("msg").value = "";
        } else {
            const data = await res.json();
            alert("✗ " + (data.error || "Failed to submit request"));
        }
    } catch (err) {
        alert("✗ Server error. Please try again.");
        console.error(err);
    }
}

function logout() {
    localStorage.removeItem("customerEmail");
    document.getElementById("portal").style.display = "none";
    document.getElementById("loginBox").style.display = "block";
    document.getElementById("email").value = "";
    document.getElementById("password").value = "";
}

// ========== PUBLIC FUNCTIONS ==========
async function req() {
    const email = document.getElementById("email").value;
    
    if (!email || !email.includes("@")) {
        alert("Please enter a valid email");
        return;
    }

    try {
        const res = await fetch("https://xvision-backend-ao7z.onrender.com/request/account", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: email })
        });

        if (res.ok) {
            alert("✓ Account request submitted! We'll contact you soon.");
            document.getElementById("email").value = "";
        } else {
            const data = await res.json();
            alert("✗ " + (data.error || "Failed to submit request"));
        }
    } catch (err) {
        alert("✗ Server error. Please try again.");
        console.error(err);
    }
}

// ========== STAFF FUNCTIONS ==========
async function staffLogin() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    if (!email || !password) {
        alert("Missing email or password");
        return;
    }

    try {
        const res = await fetch("https://xvision-backend-ao7z.onrender.com/staff/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.error || "Login failed");
            return;
        }

        // ✅ SUCCESS → SHOW STAFF PANEL
        document.getElementById("staffLoginBox").style.display = "none";
        document.getElementById("staffPanel").style.display = "block";
        
        // Store staff data
        localStorage.setItem("staffEmail", data.email);
        localStorage.setItem("staffRole", data.role);

    } catch (err) {
        alert("Server error");
        console.error(err);
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

    const res = await fetch("https://xvision-backend-ao7z.onrender.com/staff/create", {
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

// ========== UTILITY FUNCTIONS ==========
function checkHealth() {
    fetch("https://xvision-backend-ao7z.onrender.com/health")
        .then(res => res.json())
        .then(data => console.log("Backend health:", data))
        .catch(err => console.warn("Backend not responding"));
}

// Check backend health on page load
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", checkHealth);
} else {
    checkHealth();
}