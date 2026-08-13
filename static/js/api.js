// Prevent duplicate declaration of API_BASE if already defined elsewhere
if (typeof API_BASE === "undefined") {
  var API_BASE = "/api";
}

function getToken() {
  return localStorage.getItem("access");
}

function getRefreshToken() {
  return localStorage.getItem("refresh");
}

async function refreshAccessToken() {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;

  try {
    const res = await fetch("/api/token/refresh/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (res.ok) {
      const data = await res.json();
      if (data.access) {
        localStorage.setItem("access", data.access);
        return data.access;
      }
    }
  } catch (e) {
    console.error("Token refresh failed:", e);
  }
  return null;
}

async function apiRequest(endpoint, method = "GET", body = null, isRetry = false) {
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

  const url = endpoint.startsWith("http") || endpoint.startsWith("/api") ? endpoint : API_BASE + endpoint;
  let response = await fetch(url, options);

  // If 401 Unauthorized, attempt auto refresh once
  if (response.status === 401 && !isRetry) {
    const newAccessToken = await refreshAccessToken();
    if (newAccessToken) {
      options.headers.Authorization = `Bearer ${newAccessToken}`;
      response = await fetch(url, options);
    } else {
      localStorage.clear();
      window.location.href = "/login/";
      return;
    }
  }

  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return await response.json();
  }

  const text = await response.text();
  return { detail: `Server returned ${response.status}: ${text.substring(0, 200)}`, status: response.status };
}

// Global hook for navbar logout button click
document.addEventListener("DOMContentLoaded", () => {
  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      localStorage.clear();
      window.location.href = "/login/";
    });
  }
});
