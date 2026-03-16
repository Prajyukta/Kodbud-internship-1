// ── Canvas Drawing ───────────────────────────────────────────
const canvas = document.getElementById("drawCanvas");
if (canvas) {
  const ctx = canvas.getContext("2d");
  let drawing = false, lastX = 0, lastY = 0;

  ctx.fillStyle = "#000";
  ctx.fillRect(0, 0, 280, 280);
  ctx.strokeStyle = "#fff";
  ctx.lineWidth = 22;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";

  function pos(e) {
    const r = canvas.getBoundingClientRect();
    const sx = canvas.width / r.width;
    const sy = canvas.height / r.height;
    if (e.touches) {
      return { x: (e.touches[0].clientX - r.left) * sx,
               y: (e.touches[0].clientY - r.top)  * sy };
    }
    return { x: (e.clientX - r.left) * sx, y: (e.clientY - r.top) * sy };
  }

  canvas.addEventListener("mousedown",  e => { drawing = true; const p = pos(e); lastX = p.x; lastY = p.y; });
  canvas.addEventListener("mousemove",  e => {
    if (!drawing) return;
    const p = pos(e);
    ctx.beginPath(); ctx.moveTo(lastX, lastY); ctx.lineTo(p.x, p.y); ctx.stroke();
    lastX = p.x; lastY = p.y;
  });
  canvas.addEventListener("mouseup",    () => drawing = false);
  canvas.addEventListener("mouseleave", () => drawing = false);

  canvas.addEventListener("touchstart", e => { e.preventDefault(); drawing = true; const p = pos(e); lastX = p.x; lastY = p.y; });
  canvas.addEventListener("touchmove",  e => {
    e.preventDefault();
    if (!drawing) return;
    const p = pos(e);
    ctx.beginPath(); ctx.moveTo(lastX, lastY); ctx.lineTo(p.x, p.y); ctx.stroke();
    lastX = p.x; lastY = p.y;
  });
  canvas.addEventListener("touchend", () => drawing = false);
}

function clearCanvas() {
  const canvas = document.getElementById("drawCanvas");
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = "#000";
  ctx.fillRect(0, 0, 280, 280);
  document.getElementById("resultBox").innerHTML =
    `<p class="placeholder">Draw a digit and click Predict</p>`;
  for (let i = 0; i < 10; i++) {
    document.getElementById("bar" + i).style.width = "0%";
    document.getElementById("pct" + i).textContent  = "0%";
  }
}
