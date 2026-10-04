const App = {
  init: () => {
    App.setupThemeToggle();
    App.updateUserInfo();
    App.highlightActiveNav();
  },

  setupThemeToggle: () => {
    const theme = localStorage.getItem("portflow_theme") || "light";
    document.documentElement.setAttribute("data-theme", theme);
    const themeBtn = document.getElementById("themeToggleBtn");
    if (themeBtn) {
      themeBtn.innerHTML = theme === "dark" ? '<i class="bi bi-sun-fill"></i> Light Mode' : '<i class="bi bi-moon-stars-fill"></i> Dark Mode';
      themeBtn.onclick = () => {
        const current = document.documentElement.getAttribute("data-theme");
        const next = current === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", next);
        localStorage.setItem("portflow_theme", next);
        themeBtn.innerHTML = next === "dark" ? '<i class="bi bi-sun-fill"></i> Light Mode' : '<i class="bi bi-moon-stars-fill"></i> Dark Mode';
      };
    }
  },

  updateUserInfo: () => {
    const userDisplay = document.getElementById("userDisplay");
    const roleBadge = document.getElementById("roleBadge");
    if (userDisplay && Auth.isAuthenticated()) {
      userDisplay.textContent = Auth.getUsername();
    }
    if (roleBadge && Auth.isAuthenticated()) {
      roleBadge.textContent = Auth.getRole();
    }
  },

  highlightActiveNav: () => {
    const currentPage = window.location.pathname.split("/").pop() || "index.html";
    document.querySelectorAll(".sidebar-nav .nav-item").forEach(item => {
      const link = item.querySelector("a");
      if (link && link.getAttribute("href") === currentPage) {
        item.classList.add("active");
      } else {
        item.classList.remove("active");
      }
    });
  },

  showToast: (message, type = "info") => {
    let container = document.getElementById("toastContainer");
    if (!container) {
      container = document.createElement("div");
      container.id = "toastContainer";
      document.body.appendChild(container);
    }

    const toastEl = document.createElement("div");
    toastEl.className = `toast align-items-center text-white bg-${type} border-0 show mb-2`;
    toastEl.setAttribute("role", "alert");
    toastEl.innerHTML = `
      <div class="d-flex">
        <div class="toast-body">${message}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    `;
    container.appendChild(toastEl);
    setTimeout(() => {
      toastEl.remove();
    }, 4000);
  },

  logout: () => {
    Auth.clearSession();
    window.location.href = "index.html";
  }
};

document.addEventListener("DOMContentLoaded", () => {
  App.init();
});
