document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("loginForm");
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const usernameInput = document.getElementById("loginUsername");
      const passwordInput = document.getElementById("loginPassword");

      const username = usernameInput ? usernameInput.value.trim() : "";
      const password = passwordInput ? passwordInput.value.trim() : "";

      if (!username || !password) {
        App.showToast("Please enter both username and password.", "warning");
        return;
      }

      const submitBtn = loginForm.querySelector("button[type='submit']");
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Signing in...`;
      }

      try {
        const res = await fetch(`${CONFIG.API_BASE_URL}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password })
        });
        
        const data = await res.json();
        
        if (!res.ok) {
          throw new Error(data.detail || "Invalid username or password.");
        }

        Auth.setSession(data.access_token, data.username, data.role);
        App.showToast("Login successful! Redirecting to Dashboard...", "success");

        setTimeout(() => { 
          window.location.href = "dashboard.html"; 
        }, 400);

      } catch (err) {
        console.error("Login Error:", err);
        App.showToast(err.message || "Could not connect to server.", "danger");
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = `<i class="bi bi-box-arrow-in-right me-2"></i>Sign In`;
        }
      }
    });
  }

  const registerForm = document.getElementById("registerForm");
  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const username = document.getElementById("regUsername").value.trim();
      const email = document.getElementById("regEmail").value.trim();
      const password = document.getElementById("regPassword").value;
      const role = document.getElementById("regRole").value;

      try {
        await API.post("/auth/register", { username, email, password, role });
        App.showToast("Registration successful! You can now log in.", "success");
        const modalEl = document.getElementById("registerModal");
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
        
        // Auto fill login form
        document.getElementById("loginUsername").value = username;
        document.getElementById("loginPassword").value = password;
      } catch (err) {
        console.error("Registration error:", err);
      }
    });
  }
});
