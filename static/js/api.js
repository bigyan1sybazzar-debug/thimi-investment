const API_BASE = "/api";

function getToken() {
  return localStorage.getItem("access");
}

async function apiRequest(endpoint, method = "GET", body = null) {
  const headers = {
    Authorization: `Bearer ${getToken()}`,
    "Content-Type": "application/json",
  };

  const options = {
    method,
    headers,
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(API_BASE + endpoint, options);

  if (response.status === 401) {
    localStorage.clear();

    window.location.href = "/";

    return;
  }

  return await response.json();
}

// Global hook for navbar logout button click
document.addEventListener("DOMContentLoaded", () => {
  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      localStorage.clear();
      window.location.href = "/";
    });
  }
});
