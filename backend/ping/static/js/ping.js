// WebSocket echo and background task demo for /api/ping/index.
(function () {
  const root = document.getElementById("ping");
  const $ = (id) => document.getElementById(id);
  const clientId = Math.random().toString(36).slice(2, 8);
  let socket = null;

  function setPill(el, text, kind) {
    el.textContent = text;
    el.className = "pill" + (kind ? " " + kind : "");
  }

  function log(message, kind) {
    const line = document.createElement("p");
    const time = document.createElement("time");
    time.textContent = new Date().toLocaleTimeString([], { hour12: false });
    line.className = kind;
    line.append(time, document.createTextNode(message));
    $("ws-log").append(line);
    $("ws-log").scrollTop = $("ws-log").scrollHeight;
  }

  // ---------------------------------------------------------------- websocket
  function wsUrl() {
    const scheme = window.location.protocol === "https:" ? "wss:" : "ws:";
    return scheme + "//" + window.location.host + root.dataset.wsPath;
  }

  function connect() {
    socket = new WebSocket(wsUrl());
    setPill($("ws-status"), "connecting", "wait");
    socket.onopen = () => {
      setPill($("ws-status"), "connected", "ok");
      $("ws-toggle").textContent = "Disconnect";
      log("Connected", "connect");
    };
    socket.onclose = (event) => {
      setPill($("ws-status"), "closed", "bad");
      $("ws-toggle").textContent = "Connect";
      log("Closed (code " + event.code + ")", "disconnect");
    };
    socket.onerror = () => log("Connection error", "error");
    socket.onmessage = (event) => log("Received: " + JSON.parse(event.data).message, "received");
  }

  $("ws-url").textContent = wsUrl();
  $("ws-send").addEventListener("click", () => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      log("Not connected", "error");
      return;
    }
    const message = "Hello from " + clientId;
    socket.send(JSON.stringify({ message: message }));
    log("Sent: " + message, "sent");
  });
  $("ws-toggle").addEventListener("click", () => {
    if (socket && socket.readyState === WebSocket.OPEN) socket.close();
    else connect();
  });
  connect();

  // ---------------------------------------------------------------- background task
  async function runTask() {
    const button = $("task-run");
    button.disabled = true;
    $("task-result").textContent = "-";
    $("task-time").textContent = "-";
    const started = performance.now();
    try {
      const job = await (await fetch(root.dataset.jobUrl)).json();
      $("task-id").textContent = job.response;
      setPill($("task-status"), "pending", "wait");
      const progressUrl = root.dataset.progressUrl.replace("TASK_ID", job.response);
      for (let attempt = 0; attempt < 60; attempt++) {
        const progress = await (await fetch(progressUrl)).json();
        if (progress.state !== "PENDING") {
          setPill($("task-status"), progress.state.toLowerCase(), progress.state === "SUCCESS" ? "ok" : "bad");
          $("task-result").textContent = JSON.stringify(progress.details);
          $("task-time").textContent = ((performance.now() - started) / 1000).toFixed(1) + " s";
          return;
        }
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
      setPill($("task-status"), "timed out", "bad");
      $("task-result").textContent = "No result after 60 s. Is the qcluster worker running?";
    } catch (error) {
      setPill($("task-status"), "error", "bad");
      $("task-result").textContent = error.message;
    } finally {
      button.disabled = false;
    }
  }
  $("task-run").addEventListener("click", runTask);
})();
