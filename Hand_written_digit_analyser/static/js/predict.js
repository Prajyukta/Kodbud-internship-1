// ── Predict from Canvas ──────────────────────────────────────
async function predictCanvas() {
  const canvas  = document.getElementById("drawCanvas");
  const dataUrl = canvas.toDataURL("image/png");
  await runPrediction({ image: dataUrl }, "POST", "/api/predict");
}

// ── Predict from File Upload ─────────────────────────────────
async function handleUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  const formData = new FormData();
  formData.append("file", file);
  const resp = await fetch("/api/predict/upload", { method: "POST", body: formData });
  const data = await resp.json();
  displayResult(data);
}

// ── Core prediction handler ───────────────────────────────────
async function runPrediction(body, method, url) {
  try {
    const resp = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await resp.json();
    displayResult(data);
  } catch (e) {
    document.getElementById("resultBox").innerHTML =
      `<p class="placeholder" style="color:#ef4444">Error: ${e.message}</p>`;
  }
}

function displayResult(data) {
  if (data.error) {
    document.getElementById("resultBox").innerHTML =
      `<p class="placeholder" style="color:#ef4444">${data.error}</p>`;
    return;
  }

  document.getElementById("resultBox").innerHTML = `
    <div class="digit-big">${data.digit}</div>
    <div class="conf-text">Confidence: <span class="conf-val">${data.confidence}%</span></div>
  `;

  // Update probability bars
  for (let i = 0; i < 10; i++) {
    const pct = data.probabilities[String(i)] || 0;
    document.getElementById("bar" + i).style.width = pct + "%";
    document.getElementById("pct" + i).textContent  = pct.toFixed(1) + "%";
  }
}

// ── Model status on load ─────────────────────────────────────
window.addEventListener("DOMContentLoaded", async () => {
  const bar = document.getElementById("statusBar");
  try {
    const resp = await fetch("/api/model/status");
    const data = await resp.json();
    if (data.loaded) {
      bar.textContent = `✅ Model ready — Test Accuracy: ${data.test_acc ?? "—"}%`;
      bar.className   = "status-bar ready";
    } else {
      bar.textContent = "⚠️ No model loaded — visit /train to train one first";
      bar.className   = "status-bar error";
    }
  } catch {
    bar.textContent = "Could not reach server";
  }
});
