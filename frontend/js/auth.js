const Auth = {
  getToken: () => localStorage.getItem("portflow_token"),
  getUsername: () => localStorage.getItem("portflow_username"),
  getRole: () => localStorage.getItem("portflow_role"),

  setSession: (token, username, role) => {
    localStorage.setItem("portflow_token", token);
    localStorage.setItem("portflow_username", username);
    localStorage.setItem("portflow_role", role);
  },

  clearSession: () => {
    localStorage.removeItem("portflow_token");
    localStorage.removeItem("portflow_username");
    localStorage.removeItem("portflow_role");
  },

  isAuthenticated: () => {
    const token = localStorage.getItem("portflow_token");
    return !!token && token !== "undefined" && token !== "null" && token.trim().length > 0;
  },

  requireAuth: () => {
    if (!Auth.isAuthenticated()) {
      window.location.href = "index.html";
    }
  },

  hasRole: (...roles) => {
    const userRole = Auth.getRole();
    if (userRole === "Administrator") return true;
    return roles.includes(userRole);
  }
};
