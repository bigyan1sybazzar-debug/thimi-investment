const API_URL = "http://127.0.0.1:8000/api/";

async function apiRequest(endpoint, method = "GET", body = null) {
  const token = localStorage.getItem("access");

  const options = {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };

  if (body) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }

  const response = await fetch(API_URL + endpoint, options);

  return response.json();
}
