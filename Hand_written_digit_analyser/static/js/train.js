// ── Training Page JS ─────────────────────────────────────────
let polling = null;

function addLog(msg, type = "log") {
  const box = document.getElementById("logBox");
  const line = document.createElement("div");
  line.className = "log-line " + type;
  const time = new Date().toLocaleTimeString();
  line.textContent = `[${time}] ${msg}`;
  box.appendChild(line);
  box.scrollTop = box.scrollHeight;
}

async function startTraining() {
  const btn       = document.getElementById("trainBtn");
  const epochs    = parseInt(document.getElementById("epochs").value);
  const batchSize = parseInt(document.getElementById("batchSize").value);

  btn.disabled = true;
  btn.textContent = "⏳ Training…";
  document.getElementById("progressWrap").style.display = "block";
  document.getElementById("statGrid").style.display     = "none";

  addLog(`Starting training — epochs: ${epochs}, batch: ${batchSize}`, "accent");

  try {
    const resp = await fetch("/api/train", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ epochs, batch_size: batchSize }),
    });
    const data = await resp.json();
    if (data.error) { addLog("Error: " + data.error, "error"); btn.disabled = false; return; }
    addLog("Training started on server…", "log");
    pollStatus();
  } catch (e) {
    addLog("Request failed: " + e.message, "error");
    btn.disabled = false;
  }
}

function pollStatus() {
  let lastMsg = "";
  polling = setInterval(async () => {
    try {
      const resp = await fetch("/api/train/status");
      const data = await resp.json();

      if (data.message !== lastMsg) {
        addLog(data.message, data.running ? "log" : "success");
        lastMsg = data.message;
      }

      document.getElementById("progressMsg").textContent = data.message;

      if (!data.running) {
        clearInterval(polling);
        document.getElementById("trainBtn").disabled    = false;
        document.getElementById("trainBtn").textContent = "🔄 Retrain";
        document.getElementById("progressFill").style.width = "100%";

        // Fetch final stats
        const sr = await fetch("/api/model/status");
        const sd = await sr.json();
        if (sd.test_acc) {
          document.getElementById("statGrid").style.display = "grid";
          document.getElementById("statAcc").textContent    = sd.test_acc + "%";
          document.getElementById("statLoss").textContent   = sd.test_loss;
        }
      }
    } catch { /* ignore transient errors */ }
  }, 2000);
}
