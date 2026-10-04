document.addEventListener("DOMContentLoaded", async () => {
  Auth.requireAuth();

  const canvas = document.getElementById("simCanvas");
  const ctx = canvas ? canvas.getContext("2d") : null;
  const speedSlider = document.getElementById("speedSlider");
  const speedDisplay = document.getElementById("speedDisplay");

  let simState = { status: "Stopped", speed: 1.0, ticks: 0, ships: [], ports: [] };

  async function initSimulationPage() {
    try {
      const ports = await API.get("/ports");
      simState.ports = ports;
      const statusData = await API.get("/simulation/status");
      updateUIStatus(statusData.status, statusData.ticks_elapsed, statusData.speed_multiplier);
    } catch (err) {
      console.error("Init simulation error:", err);
    }
  }

  function updateUIStatus(status, ticks, speed) {
    simState.status = status;
    simState.ticks = ticks;
    simState.speed = speed;

    const statusBadge = document.getElementById("simStateBadge");
    if (statusBadge) {
      statusBadge.textContent = status.toUpperCase();
      statusBadge.className = `badge fs-6 bg-${status === 'Running' ? 'success' : (status === 'Paused' ? 'warning' : 'secondary')}`;
    }

    const ticksEl = document.getElementById("simTicksDisplay");
    if (ticksEl) ticksEl.textContent = ticks;

    if (speedSlider) speedSlider.value = speed;
    if (speedDisplay) speedDisplay.textContent = `${speed}x`;
  }

  window.sendSimControl = async (action) => {
    try {
      const speed = speedSlider ? parseFloat(speedSlider.value) : 1.0;
      await API.post("/simulation/control", { action, speed_multiplier: speed });
      App.showToast(`Simulation command '${action}' sent`, "info");
      const statusData = await API.get("/simulation/status");
      updateUIStatus(statusData.status, statusData.ticks_elapsed, statusData.speed_multiplier);
    } catch (err) {}
  };

  if (speedSlider) {
    speedSlider.addEventListener("input", () => {
      if (speedDisplay) speedDisplay.textContent = `${speedSlider.value}x`;
    });
    speedSlider.addEventListener("change", () => {
      sendSimControl(simState.status === "Running" ? "resume" : "pause");
    });
  }

  // Render 2D Cartesian Grid & Moving Ships
  function renderCanvas() {
    if (!canvas || !ctx) return;

    const width = canvas.width;
    const height = canvas.height;

    // Clear background
    ctx.fillStyle = "#090d16";
    ctx.fillRect(0, 0, width, height);

    // Draw Grid Lines
    ctx.strokeStyle = "rgba(51, 65, 85, 0.3)";
    ctx.lineWidth = 1;
    for (let x = 0; x < width; x += 50) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, height); ctx.stroke();
    }
    for (let y = 0; y < height; y += 50) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(width, y); ctx.stroke();
    }

    // Scale Cartesian coords (e.g., 0-150 range mapped to canvas size)
    const scaleX = width / 150;
    const scaleY = height / 120;

    // Draw Ports
    simState.ports.forEach(p => {
      const px = p.x_coord * scaleX;
      const py = p.y_coord * scaleY;

      // Pulse circle (Teal)
      ctx.beginPath();
      ctx.arc(px, py, 18, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(15, 118, 110, 0.2)";
      ctx.fill();

      // Outer ring
      ctx.beginPath();
      ctx.arc(px, py, 10, 0, Math.PI * 2);
      ctx.strokeStyle = "#0f766e";
      ctx.lineWidth = 2;
      ctx.stroke();

      // Center dot
      ctx.beginPath();
      ctx.arc(px, py, 4, 0, Math.PI * 2);
      ctx.fillStyle = "#14b8a6";
      ctx.fill();

      // Label
      ctx.fillStyle = "#f8fafc";
      ctx.font = "bold 12px Inter, sans-serif";
      ctx.fillText(p.name, px + 14, py + 4);
    });

    // Draw Ships
    simState.ships.forEach(s => {
      if (s.x === null || s.y === null) return;
      const sx = s.x * scaleX;
      const sy = s.y * scaleY;

      // Ship Icon / Marker
      ctx.beginPath();
      ctx.arc(sx, sy, 8, 0, Math.PI * 2);
      ctx.fillStyle = s.status === "In Transit" ? "#10b981" : (s.status === "Maintenance" ? "#ef4444" : "#f59e0b");
      ctx.fill();
      ctx.strokeStyle = "#ffffff";
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Fuel Bar
      const fuelPct = s.fuel / s.fuel_capacity;
      ctx.fillStyle = "rgba(0,0,0,0.6)";
      ctx.fillRect(sx - 15, sy - 18, 30, 5);
      ctx.fillStyle = fuelPct > 0.2 ? "#10b981" : "#ef4444";
      ctx.fillRect(sx - 15, sy - 18, 30 * fuelPct, 5);

      // Ship Name Label
      ctx.fillStyle = "#e2e8f0";
      ctx.font = "11px Inter, sans-serif";
      ctx.fillText(`${s.name} (${s.fuel.toFixed(0)}L)`, sx + 12, sy + 4);
    });

    requestAnimationFrame(renderCanvas);
  }

  await initSimulationPage();
  renderCanvas();

  SimulationWS.connect();
  SimulationWS.subscribe(data => {
    if (data.type === "TICK") {
      updateUIStatus(data.status, data.ticks, simState.speed);
      simState.ships = data.ships;

      // Update live event log
      const logBox = document.getElementById("simLiveLogs");
      if (logBox && data.ships) {
        const inTransit = data.ships.filter(s => s.status === "In Transit");
        logBox.innerHTML = inTransit.map(s => `
          <div class="mb-1 text-sm"><i class="bi bi-water text-teal me-2"></i>Ship <strong>${s.name}</strong> moving at (${s.x.toFixed(1)}, ${s.y.toFixed(1)}) | Fuel: ${s.fuel.toFixed(1)} L</div>
        `).join("") || `<div class="text-muted text-sm">No ships currently in transit.</div>`;
      }
    }
  });
});
