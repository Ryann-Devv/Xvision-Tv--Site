async function staffLogin() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  if (!email || !password) {
    alert("Missing email or password");
    return;
  }

  try {
    const res = await fetch("https://YOUR-RENDER-URL.onrender.com/staff/login", {
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
