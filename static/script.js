async function register() {
  const name = document.getElementById("regName").value;
  const email = document.getElementById("regEmail").value;
  const password = document.getElementById("regPassword").value;

  const res = await fetch("/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password })
  });
  const data = await res.json();
  alert(data.message);
}

async function login() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  const res = await fetch("/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });
  const data = await res.json();
  alert(data.message);
}

async function submitProvider() {
  const waste_type = document.getElementById("wasteType").value;
  const quantity = parseFloat(document.getElementById("wasteQty").value);
  const location = document.getElementById("wasteLoc").value;

  const res = await fetch("/provider", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ waste_type, quantity, location })
  });
  const data = await res.json();
  alert(data.message);
}

async function submitReceiver() {
  const resource_needed = document.getElementById("resType").value;
  const quantity = parseFloat(document.getElementById("resQty").value);
  const location = document.getElementById("resLoc").value;

  const res = await fetch("/receiver", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resource_needed, quantity, location })
  });
  const data = await res.json();
  alert(data.message);
}

async function findMatch() {
  const res = await fetch("/match");
  const data = await res.json();
  const out = document.getElementById("matchResults");

  if (data.status === "success") {
    out.innerText = JSON.stringify(data.matches, null, 2);
  } else {
    out.innerText = data.message;
  }
}
