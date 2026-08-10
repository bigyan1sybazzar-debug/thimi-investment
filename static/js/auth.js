const API_BASE = "/api";

// Auto-redirect if already logged in
async function checkCurrentSession() {
  const token = localStorage.getItem("access");
  if (token) {
    try {
      const response = await fetch(`${API_BASE}/accounts/me/`, {
        method: "GET",
        headers: {
          Authorization: "Bearer " + token,
        },
      });
      if (response.ok) {
        const user = await response.json();
        if (user.is_staff || user.is_superuser) {
          window.location.href = "/admin-dashboard/";
        } else if (user.is_member) {
          window.location.href = "/member/dashboard/";
        }
      } else {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
      }
    } catch (error) {
      console.error("Session check failed:", error);
    }
  }
}

// Run session check on script load
checkCurrentSession();

document
  .getElementById("loginForm")
  .addEventListener("submit", async function (e) {
    e.preventDefault();

    const username = document.getElementById("username").value;

    const password = document.getElementById("password").value;

    try {
      // Login request
      const response = await fetch(`${API_BASE}/accounts/login/`, {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          username: username,
          password: password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Save JWT tokens

        localStorage.setItem("access", data.access);

        localStorage.setItem("refresh", data.refresh);

        // Get current user details

        const meResponse = await fetch(`${API_BASE}/accounts/me/`, {
          method: "GET",

          headers: {
            Authorization: "Bearer " + data.access,
          },
        });

        const user = await meResponse.json();

        console.log("CURRENT USER:", user);

        // Redirect based on role

        if (user.is_staff || user.is_superuser) {
          window.location.href = "/admin-dashboard/";
        } else if (user.is_member) {
          window.location.href = "/member/dashboard/";
        } else {
          alert("No user role assigned");
        }
      } else {
        alert(data.detail || "Invalid username or password");
      }
    } catch (error) {
      console.error("Login Error:", error);

      alert("Server connection failed");
    }
  });
