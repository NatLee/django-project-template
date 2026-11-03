// "JWT login" asks the token endpoint instead of submitting the session form.
(function () {
  const form = document.getElementById("login-form");
  const message = document.getElementById("message");

  function show(text, kind) {
    message.textContent = text;
    message.className = "note " + kind;
    message.hidden = false;
  }

  document.getElementById("jwt-login").addEventListener("click", async () => {
    if (!form.reportValidity()) return;
    try {
      const response = await fetch(form.dataset.tokenUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: form.username.value, password: form.password.value }),
      });
      const data = await response.json();
      if (!response.ok || !data.access_token) {
        show(data.detail || "JWT login failed. Check the username and password.", "bad");
        return;
      }
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      show("JWT login worked. Going back to the dashboard...", "ok");
      window.location.href = form.dataset.dashboardUrl;
    } catch (error) {
      show("JWT login failed: " + error.message, "bad");
    }
  });
})();
