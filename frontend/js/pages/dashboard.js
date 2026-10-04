document.addEventListener("DOMContentLoaded", async () => {
  Auth.requireAuth();

  async function loadDashboardData() {
    try {
      const analytics = await API.get("/reports/analytics");
      const simStatus = await API.get("/simulation/status");
      const movements = await API.get("/reports/movement-history");

      // Update metric card numbers
      if (document.getElementById("statPorts")) document.getElementById("statPorts").textContent = analytics.summary.total_ports;
      if (document.getElementById("statActiveShips")) document.getElementById("statActiveShips").textContent = analytics.summary.total_ships;
      if (document.getElementById("statDockedShips")) document.getElementById("statDockedShips").textContent = analytics.summary.docked_ships;
      if (document.getElementById("statTransitShips")) document.getElementById("statTransitShips").textContent = analytics.summary.in_transit_ships;
      if (document.getElementById("statContainers")) document.getElementById("statContainers").textContent = analytics.summary.total_containers;
      if (document.getElementById("statFuel")) document.getElementById("statFuel").textContent = `${analytics.summary.total_fuel_consumed} L`;

      const simStatusBadge = document.getElementById("statSimStatus");
      if (simStatusBadge) {
        simStatusBadge.textContent = simStatus.status;
        simStatusBadge.className = `badge bg-${simStatus.status === 'Running' ? 'success' : (simStatus.status === 'Paused' ? 'warning' : 'secondary')}`;
      }

      // Render Port Occupancy Table (HTML replacement for bar chart)
      renderPortOccupancy(analytics.port_utilization);

      // Render Container Type List (HTML replacement for doughnut chart)
      renderContainerTypes(analytics.container_distribution, analytics.summary.total_containers);

      // Render Movement Logs Table
      const movementBody = document.getElementById("movementLogsBody");
      if (movementBody) {
        if (movements && movements.length > 0) {
          movementBody.innerHTML = movements.slice(0, 5).map(m => `
            <tr>
              <td class="fw-semibold text-dark">${m.ship_name}</td>
              <td><span class="badge bg-light text-dark border">${m.origin_port}</span> &rarr; <span class="badge bg-dark">${m.destination_port}</span></td>
              <td class="small text-secondary">${m.details}</td>
              <td class="small text-muted">${m.timestamp}</td>
            </tr>
          `).join("");
        } else {
          movementBody.innerHTML = `<tr><td colspan="4" class="text-center text-muted py-3">No recent movement activity recorded.</td></tr>`;
        }
      }

    } catch (err) {
      console.error("Dashboard data load error:", err);
    }
  }

  function renderPortOccupancy(portData) {
    const body = document.getElementById("portOccupancyBody");
    if (!body || !portData) return;

    body.innerHTML = portData.map(p => {
      const pct = p.utilization_pct || 0;
      let badgeClass = "bg-success";
      if (pct > 75) badgeClass = "bg-danger";
      else if (pct > 50) badgeClass = "bg-warning text-dark";

      return `
        <tr>
          <td class="fw-semibold text-dark">${p.name}</td>
          <td>${p.docked_ships} / ${p.dock_capacity} Ships</td>
          <td style="min-width: 140px;">
            <div class="d-flex align-items-center gap-2">
              <div class="progress flex-grow-1" style="height: 8px;">
                <div class="progress-bar ${badgeClass}" style="width: ${pct}%"></div>
              </div>
              <small class="fw-bold">${pct}%</small>
            </div>
          </td>
          <td><span class="badge ${badgeClass}">${pct === 100 ? 'Full' : (pct > 0 ? 'Active' : 'Available')}</span></td>
        </tr>
      `;
    }).join("");
  }

  function renderContainerTypes(dist, total) {
    const list = document.getElementById("containerTypeList");
    if (!list || !dist) return;

    const types = [
      { name: "Basic Containers", key: "Basic", color: "bg-dark" },
      { name: "Heavy Containers", key: "Heavy", color: "bg-danger" },
      { name: "Refrigerated", key: "Refrigerated", color: "bg-success" },
      { name: "Liquid Containers", key: "Liquid", color: "bg-warning text-dark" }
    ];

    list.innerHTML = types.map(t => {
      const count = dist[t.key] || 0;
      const pct = total > 0 ? Math.round((count / total) * 100) : 0;

      return `
        <div class="mb-3">
          <div class="d-flex justify-content-between align-items-center mb-1">
            <span class="small fw-medium">${t.name}</span>
            <span class="small fw-bold">${count} (${pct}%)</span>
          </div>
          <div class="progress" style="height: 8px;">
            <div class="progress-bar ${t.color}" style="width: ${pct}%"></div>
          </div>
        </div>
      `;
    }).join("");
  }

  await loadDashboardData();
  
  if (typeof SimulationWS !== 'undefined') {
    SimulationWS.connect();
    SimulationWS.subscribe(data => {
      if (data.type === "TICK" || data.type === "EVENT") {
        loadDashboardData();
      }
    });
  }
});
