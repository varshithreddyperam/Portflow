const API = {
  async request(endpoint, method = "GET", body = null) {
    const headers = { "Content-Type": "application/json" };
    const token = Auth.getToken();
    if (token && token !== "undefined" && token !== "null" && token.trim().length > 0) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const options = { method, headers };
    if (body) {
      options.body = JSON.stringify(body);
    }

    try {
      const response = await fetch(`${CONFIG.API_BASE_URL}${endpoint}`, options);

      if (response.status === 401) {
        Auth.clearSession();
        window.location.href = "index.html";
        throw new Error("Session expired or invalid login. Please log in again.");
      }

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "An unexpected API error occurred.");
      }
      return data;
    } catch (err) {
      if (typeof App !== 'undefined' && App.showToast) {
        App.showToast(err.message, "danger");
      }
      throw err;
    }
  },

  get: (endpoint) => API.request(endpoint, "GET"),
  post: (endpoint, body) => API.request(endpoint, "POST", body),
  put: (endpoint, body) => API.request(endpoint, "PUT", body),
  delete: (endpoint) => API.request(endpoint, "DELETE")
};
