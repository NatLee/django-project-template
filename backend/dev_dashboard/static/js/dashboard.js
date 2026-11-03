// Login playground: shows the JWT stored in this browser and the linked social accounts.
(function () {
  const root = document.getElementById("dashboard");
  const urls = {
    refresh: root.dataset.tokenRefreshUrl,
    verify: root.dataset.tokenVerifyUrl,
    accounts: root.dataset.socialAccountsUrl,
  };
  const $ = (id) => document.getElementById(id);
  const signedOutHint = "Sign in with a JWT to see linked accounts.";

  function setPill(el, text, kind) {
    el.textContent = text;
    el.className = "pill" + (kind ? " " + kind : "");
  }

  function showListMessage(text) {
    const item = document.createElement("li");
    item.className = "muted";
    item.textContent = text;
    $("social-accounts").replaceChildren(item);
  }

  async function postJSON(url, body) {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || JSON.stringify(data));
    return data;
  }

  function authHeaders() {
    return { Authorization: "Bearer " + localStorage.getItem("access_token") };
  }

  // Refresh the access token with the stored refresh token, then verify it.
  async function refreshJWT() {
    const refresh = localStorage.getItem("refresh_token");
    if (!refresh) {
      setPill($("jwt-status"), "no token");
      $("token").textContent = "No token stored in this browser. Use JWT login on the sign-in page, or a social login.";
      $("jwt-result").textContent = "";
      return false;
    }
    try {
      const data = await postJSON(urls.refresh, { refresh: refresh });
      localStorage.setItem("access_token", data.access_token);
      await postJSON(urls.verify, { token: data.access_token });
      $("token").textContent = "Bearer " + data.access_token;
      $("jwt-result").textContent = "Token refreshed and verified just now.";
      setPill($("jwt-status"), "valid", "ok");
      return true;
    } catch (error) {
      $("jwt-result").textContent = "Refresh failed: " + error.message;
      setPill($("jwt-status"), "expired", "bad");
      return false;
    }
  }

  async function loadSocialAccounts() {
    if (!localStorage.getItem("access_token")) return;
    try {
      const response = await fetch(urls.accounts, { headers: authHeaders() });
      if (!response.ok) throw new Error("HTTP " + response.status);
      const data = await response.json();
      const accounts = data.social_accounts;
      setPill($("accounts-count"), String(accounts.length), accounts.length ? "ok" : "");
      if (!accounts.length) {
        showListMessage("No social account linked to " + data.username + " yet.");
        return;
      }
      const items = accounts.map((account) => {
        const item = document.createElement("li");
        const label = document.createElement("span");
        const provider = document.createElement("strong");
        const uid = document.createElement("code");
        provider.textContent = account.provider + " ";
        uid.textContent = account.uid;
        label.append(provider, uid);
        const button = document.createElement("button");
        button.className = "btn small danger";
        button.textContent = "Unlink";
        button.addEventListener("click", () => unlink(account.id));
        item.append(label, button);
        return item;
      });
      $("social-accounts").replaceChildren(...items);
    } catch (error) {
      showListMessage("Could not load linked accounts (" + error.message + ").");
    }
  }

  async function unlink(accountId) {
    const response = await fetch(urls.accounts, {
      method: "DELETE",
      headers: { ...authHeaders(), "Content-Type": "application/json" },
      body: JSON.stringify({ account_id: accountId }),
    });
    const data = await response.json();
    $("jwt-result").textContent = data.message || data.error;
    loadSocialAccounts();
  }

  function forgetToken() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    refreshJWT();
    showListMessage(signedOutHint);
    setPill($("accounts-count"), "-");
  }

  // Social login runs in a popup; the popup page sets loginStatus=success when done.
  for (const link of document.querySelectorAll(".social-popup")) {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      localStorage.removeItem("loginStatus");
      window.open(link.href, "socialLogin", "width=600,height=640");
      const timer = setInterval(() => {
        if (localStorage.getItem("loginStatus") === "success") {
          clearInterval(timer);
          localStorage.removeItem("loginStatus");
          refreshJWT().then(loadSocialAccounts);
        }
      }, 1000);
    });
  }

  $("jwt-refresh").addEventListener("click", () => refreshJWT().then(loadSocialAccounts));
  $("jwt-clear").addEventListener("click", forgetToken);
  refreshJWT().then(loadSocialAccounts);
})();
