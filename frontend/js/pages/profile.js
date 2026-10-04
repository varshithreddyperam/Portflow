document.addEventListener("DOMContentLoaded", async () => {
  Auth.requireAuth();

  try {
    const user = await API.get("/auth/me");
    document.getElementById("profUsername").value = user.username;
    document.getElementById("profEmail").value = user.email;
    document.getElementById("profFullName").value = user.full_name || "";
    document.getElementById("profRoleBadge").textContent = user.role;
  } catch (err) {}

  const pwdForm = document.getElementById("changePasswordForm");
  if (pwdForm) {
    pwdForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const oldPassword = document.getElementById("oldPassword").value;
      const newPassword = document.getElementById("newPassword").value;
      const confirmPassword = document.getElementById("confirmPassword").value;

      if (newPassword !== confirmPassword) {
        App.showToast("New passwords do not match!", "warning");
        return;
      }

      try {
        await API.post("/auth/change-password", { old_password: oldPassword, new_password: newPassword });
        App.showToast("Password updated successfully!", "success");
        pwdForm.reset();
      } catch (err) {}
    });
  }
});
