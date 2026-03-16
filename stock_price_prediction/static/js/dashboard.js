// ============================================================
//   StockSeer — Dashboard JavaScript
// ============================================================

let currentTicker  = null;
let currentPeriod  = "2y";
let chartData      = null;
let priceChart     = null;
let volumeChart    = null;
let rsiChart       = null;
let predChart      = null;

const CHART_DEFAULTS = {
  responsive: true,
  maintainAspectRatio: false,
  animation: { duration: 600 },
  plugins: { legend: { display: false }, tooltip: { mode: "index", intersect: false } },
  scales: {
    x: {
      type: "time",
      time: { unit: "month", tooltipFormat: "MMM d, yyyy" },
      grid: { color: "rgba(37,44,61,0.8)" },
      ticks: { color: "#5a6480", maxTicksLimit: 8, font: { size: 10 } },
    },
    y: {
      grid: { color: "rgba(37,44,61,0.8)" },
      ticks: { color: "#5a6480", font: { size: 10 } },
    },
  },
};

// ── Period buttons ────────────────────────────────────────────
document.querySelectorAll(".period-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".period-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    currentPeriod = btn.dataset.period;
    if (currentTicker) loadStock(currentTicker);
  });
});

// ── Quick load ────────────────────────────────────────────────
function quickLoad(ticker) {
  document.getElementById("tickerInput").value = ticker;
  loadStock(ticker);
}

// ── Main stock load ───────────────────────────────────────────
async function loadStock(ticker) {
  const input = document.getElementById("tickerInput");
  ticker = (ticker || input.value).trim().toUpperCase();
  if (!ticker) return;

  currentTicker = ticker;
  showLoading("Fetching data for " + ticker + "…");

  try {
    const resp = await fetch("/api/stock", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ticker, period: currentPeriod }),
    });
    const data = await resp.json();
    if (data.error) throw new Error(data.error);

    chartData = data.chart;
    renderInfoBar(data);
    renderCharts(data.chart);
    document.getElementById("predictBtn").disabled = false;

    document.getElementById("welcomeCard").style.display = "none";
    document.getElementById("chartsArea").style.display  = "grid";
    document.getElementById("stockInfoBar").style.display = "flex";

  } catch(e) {
    alert("Error: " + e.message);
  } finally {
    hideLoading();
  }
}

// ── Info bar ──────────────────────────────────────────────────
function renderInfoBar(data) {
  const s = data.summary;
  document.getElementById("stockTickerBig").textContent = data.ticker;
  document.getElementById("stockNameText").textContent  = data.info.name || data.ticker;
  document.getElementById("stockPrice").textContent     = `$${s.current.toFixed(2)}`;

  const changeEl = document.getElementById("stockChange");
  const sign = s.change >= 0 ? "+" : "";
  changeEl.textContent = `${sign}${s.change.toFixed(2)} (${sign}${s.change_pct.toFixed(2)}%)`;
  changeEl.className   = "stock-change " + (s.change >= 0 ? "up" : "down");

  document.getElementById("stat52H").textContent = `$${s.high_52w}`;
  document.getElementById("stat52L").textContent = `$${s.low_52w}`;
  document.getElementById("statVol").textContent  = fmtVolume(s.avg_vol);
  document.getElementById("statDp").textContent   = s.data_points;
}

// ── Render all charts ─────────────────────────────────────────
function renderCharts(d) {
  const dates = d.dates.map(s => new Date(s));

  // ── Price chart ──────────────────────────────────────────
  if (priceChart) priceChart.destroy();
  const priceCtx = document.getElementById("priceChart").getContext("2d");

  const gradClose = priceCtx.createLinearGradient(0, 0, 0, 220);
  gradClose.addColorStop(0, "rgba(15,212,180,0.2)");
  gradClose.addColorStop(1, "rgba(15,212,180,0)");

  priceChart = new Chart(priceCtx, {
    type: "line",
    data: {
      labels: dates,
      datasets: [
        {
          id: "close", label: "Close",
          data: d.close, borderColor: "#0fd4b4", borderWidth: 2,
          backgroundColor: gradClose, fill: true,
          pointRadius: 0, tension: 0.3,
        },
        {
          id: "ma20", label: "MA 20",
          data: d.ma_20, borderColor: "#f0b429", borderWidth: 1.5,
          borderDash: [], pointRadius: 0, fill: false, tension: 0.3,
          hidden: true,
        },
        {
          id: "ma50", label: "MA 50",
          data: d.ma_50, borderColor: "#818cf8", borderWidth: 1.5,
          pointRadius: 0, fill: false, tension: 0.3,
          hidden: true,
        },
        {
          id: "bb_upper", label: "BB Upper",
          data: d.bb_upper, borderColor: "rgba(240,82,82,0.5)", borderWidth: 1,
          borderDash: [4, 3], pointRadius: 0, fill: false,
          hidden: true,
        },
        {
          id: "bb_lower", label: "BB Lower",
          data: d.bb_lower, borderColor: "rgba(15,186,129,0.5)", borderWidth: 1,
          borderDash: [4, 3], pointRadius: 0, fill: false,
          hidden: true,
        },
      ],
    },
    options: {
      ...CHART_DEFAULTS,
      plugins: {
        ...CHART_DEFAULTS.plugins,
        tooltip: {
          mode: "index", intersect: false,
          callbacks: { label: ctx => `${ctx.dataset.label}: $${Number(ctx.raw).toFixed(2)}` },
        },
      },
    },
  });

  // ── Volume chart ─────────────────────────────────────────
  if (volumeChart) volumeChart.destroy();
  const volCtx = document.getElementById("volumeChart").getContext("2d");
  volumeChart = new Chart(volCtx, {
    type: "bar",
    data: {
      labels: dates,
      datasets: [{
        label: "Volume",
        data: d.volume,
        backgroundColor: "rgba(129,140,248,0.3)",
        borderColor: "rgba(129,140,248,0.6)",
        borderWidth: 0,
        borderRadius: 1,
      }],
    },
    options: {
      ...CHART_DEFAULTS,
      plugins: { ...CHART_DEFAULTS.plugins,
        tooltip: { callbacks: { label: ctx => `Vol: ${fmtVolume(ctx.raw)}` } },
      },
    },
  });

  // ── RSI chart ─────────────────────────────────────────────
  if (rsiChart) rsiChart.destroy();
  const rsiCtx = document.getElementById("rsiChart").getContext("2d");
  rsiChart = new Chart(rsiCtx, {
    type: "line",
    data: {
      labels: dates,
      datasets: [
        {
          label: "RSI", data: d.rsi,
          borderColor: "#f0b429", borderWidth: 1.5,
          pointRadius: 0, fill: false, tension: 0.3,
        },
        {
          label: "Overbought (70)",
          data: Array(dates.length).fill(70),
          borderColor: "rgba(240,82,82,0.4)", borderWidth: 1,
          borderDash: [4, 3], pointRadius: 0, fill: false,
        },
        {
          label: "Oversold (30)",
          data: Array(dates.length).fill(30),
          borderColor: "rgba(15,186,129,0.4)", borderWidth: 1,
          borderDash: [4, 3], pointRadius: 0, fill: false,
        },
      ],
    },
    options: {
      ...CHART_DEFAULTS,
      scales: {
        ...CHART_DEFAULTS.scales,
        y: { ...CHART_DEFAULTS.scales.y, min: 0, max: 100 },
      },
    },
  });
}

// ── Toggle price chart lines ──────────────────────────────────
function toggleLine(btn, id) {
  btn.classList.toggle("active");
  if (!priceChart) return;

  const idMap = { close: 0, ma20: 1, ma50: 2, bb: [3, 4] };
  const idx   = idMap[id];

  if (Array.isArray(idx)) {
    idx.forEach(i => {
      priceChart.data.datasets[i].hidden = !btn.classList.contains("active");
    });
  } else {
    priceChart.data.datasets[idx].hidden = !btn.classList.contains("active");
  }
  priceChart.update();
}

// ── Run prediction ────────────────────────────────────────────
async function runPrediction() {
  if (!currentTicker) return;

  const model        = document.querySelector("input[name='model']:checked").value;
  const forecastDays = parseInt(document.getElementById("forecastSlider").value);

  const loaderMsg = model === "lstm"
    ? "Training LSTM model… (this may take 1–2 min)"
    : "Running Linear Regression…";
  showLoading(loaderMsg);
  document.getElementById("predictBtn").disabled = true;

  try {
    const resp = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ticker: currentTicker, period: currentPeriod, model, forecast_days: forecastDays }),
    });
    const data = await resp.json();
    if (data.error) throw new Error(data.error);

    renderPrediction(data.result);

  } catch(e) {
    alert("Prediction error: " + e.message);
  } finally {
    hideLoading();
    document.getElementById("predictBtn").disabled = false;
  }
}

// ── Render prediction results ─────────────────────────────────
function renderPrediction(result) {
  // Metrics
  document.getElementById("metricsSection").style.display = "block";
  document.getElementById("mRmse").textContent = result.metrics.rmse;
  document.getElementById("mMae").textContent  = result.metrics.mae;
  document.getElementById("mR2").textContent   = result.metrics.r2;
  document.getElementById("mMape").textContent = result.metrics.mape + "%";

  // Next day card
  const nextDayCard = document.getElementById("nextDayCard");
  nextDayCard.style.display = "block";
  document.getElementById("ndPrice").textContent = `$${result.next_day_pred}`;
  document.getElementById("ndModel").textContent = result.model_type;

  const diff = result.next_day_pred - result.last_price;
  const pct  = (diff / result.last_price) * 100;
  const sign = diff >= 0 ? "+" : "";
  const ndEl = document.getElementById("ndChange");
  ndEl.textContent = `${sign}${diff.toFixed(2)} (${sign}${pct.toFixed(2)}%) vs last close`;
  ndEl.className   = "nd-change " + (diff >= 0 ? "up" : "down");

  // Prediction chart
  document.getElementById("predChartSection").style.display = "block";
  renderPredChart(result);
}

function renderPredChart(result) {
  if (predChart) predChart.destroy();
  const ctx = document.getElementById("predChart").getContext("2d");

  const testDates   = result.test_dates.map(s => new Date(s));
  const futureDates = result.future_dates.map(s => new Date(s));

  predChart = new Chart(ctx, {
    type: "line",
    data: {
      datasets: [
        {
          label: "Actual",
          data: testDates.map((d, i) => ({ x: d, y: result.test_actual[i] })),
          borderColor: "#0fd4b4", borderWidth: 1.5,
          pointRadius: 0, fill: false, tension: 0.3,
        },
        {
          label: "Predicted",
          data: testDates.map((d, i) => ({ x: d, y: result.test_pred[i] })),
          borderColor: "#f0b429", borderWidth: 1.5,
          borderDash: [4, 3], pointRadius: 0, fill: false, tension: 0.3,
        },
        {
          label: "Forecast",
          data: futureDates.map((d, i) => ({ x: d, y: result.future_pred[i] })),
          borderColor: "#f05252", borderWidth: 2,
          pointRadius: 0, fill: false, tension: 0.3,
        },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      animation: { duration: 500 },
      plugins: {
        legend: {
          display: true,
          labels: { color: "#5a6480", font: { size: 9 }, boxWidth: 14 },
        },
        tooltip: { mode: "index", intersect: false },
      },
      scales: {
        x: {
          type: "time",
          time: { unit: "month", tooltipFormat: "MMM d, yyyy" },
          grid: { color: "rgba(37,44,61,0.8)" },
          ticks: { color: "#5a6480", maxTicksLimit: 5, font: { size: 9 } },
        },
        y: {
          grid: { color: "rgba(37,44,61,0.8)" },
          ticks: { color: "#5a6480", font: { size: 9 },
            callback: v => "$" + v.toFixed(0) },
        },
      },
    },
  });
}

// ── CSV upload ────────────────────────────────────────────────
async function uploadCSV(event) {
  const file = event.target.files[0];
  if (!file) return;
  await uploadFile(file);
}

function handleDrop(event) {
  event.preventDefault();
  const file = event.dataTransfer.files[0];
  if (file) uploadFile(file);
}

async function uploadFile(file) {
  showLoading("Processing CSV…");
  const formData = new FormData();
  formData.append("file", file);

  try {
    const resp = await fetch("/api/upload", { method: "POST", body: formData });
    const data = await resp.json();
    if (data.error) throw new Error(data.error);

    currentTicker = data.ticker;
    chartData     = data.chart;
    renderInfoBar(data);
    renderCharts(data.chart);
    document.getElementById("predictBtn").disabled = false;
    document.getElementById("welcomeCard").style.display = "none";
    document.getElementById("chartsArea").style.display  = "grid";
    document.getElementById("stockInfoBar").style.display = "flex";

  } catch(e) {
    alert("Upload error: " + e.message);
  } finally {
    hideLoading();
  }
}

// ── Helpers ───────────────────────────────────────────────────
function showLoading(msg) {
  document.getElementById("loaderText").textContent = msg || "Loading…";
  document.getElementById("loadingOverlay").style.display = "flex";
}

function hideLoading() {
  document.getElementById("loadingOverlay").style.display = "none";
}

function fmtVolume(v) {
  if (v >= 1e9) return (v / 1e9).toFixed(1) + "B";
  if (v >= 1e6) return (v / 1e6).toFixed(1) + "M";
  if (v >= 1e3) return (v / 1e3).toFixed(1) + "K";
  return v.toString();
}
