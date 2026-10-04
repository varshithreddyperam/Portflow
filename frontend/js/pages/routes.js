document.addEventListener("DOMContentLoaded", async () => {
  Auth.requireAuth();

  const routeForm = document.getElementById("routeForm");
  const routesTableBody = document.getElementById("routesTableBody");
  const routeShipSelect = document.getElementById("routeShipSelect");
  const routeDestSelect = document.getElementById("routeDestSelect");

  async function loadRoutesAndDropdowns() {
    try {
      const routes = await API.get("/routes");
      const ships = await API.get("/ships");
      const ports = await API.get("/ports");

      if (routesTableBody) {
        routesTableBody.innerHTML = routes.map(r => `
          <tr>
            <td>#${r.id}</td>
            <td><strong>${r.ship_name}</strong></td>
            <td>${r.origin_port_name} &rarr; ${r.destination_port_name}</td>
            <td>${r.distance} Units</td>
            <td>${r.estimated_fuel} L</td>
            <td>
              <div class="progress" style="height: 12px;">
                <div class="progress-bar bg-success" style="width: ${r.progress}%">${r.progress}%</div>
              </div>
            </td>
            <td><span class="badge bg-${r.status === 'Completed' ? 'success' : (r.status === 'In Progress' ? 'primary' : 'warning')}">${r.status}</span></td>
          </tr>
        `).join("");
      }

      const dockedShips = ships.filter(s => s.status === "Docked" && s.current_port_id);
      if (routeShipSelect) {
        routeShipSelect.innerHTML = `<option value="">Select Docked Ship</option>` + dockedShips.map(s => `<option value="${s.id}">${s.name} (At Port ID ${s.current_port_id})</option>`).join("");
      }

      if (routeDestSelect) {
        routeDestSelect.innerHTML = `<option value="">Select Destination Port</option>` + ports.map(p => `<option value="${p.id}">${p.name} (${p.x_coord}, ${p.y_coord})</option>`).join("");
      }

    } catch (err) {
      console.error("Load routes error:", err);
    }
  }

  async function updatePreview() {
    const shipId = routeShipSelect.value;
    const destId = routeDestSelect.value;
    const previewBox = document.getElementById("routePreviewBox");

    if (!shipId || !destId) {
      if (previewBox) previewBox.innerHTML = `<p class="text-muted m-0">Select a ship and destination port to preview route calculations.</p>`;
      return;
    }

    try {
      const preview = await API.get(`/routes/preview?ship_id=${shipId}&destination_port_id=${destId}`);
      if (previewBox) {
        previewBox.innerHTML = `
          <div class="row text-center">
            <div class="col-md-3">
              <span class="text-muted">Origin &rarr; Dest</span><br>
              <strong>${preview.origin_port} &rarr; ${preview.destination_port}</strong>
            </div>
            <div class="col-md-3">
              <span class="text-muted">Cartesian Distance</span><br>
              <strong class="text-primary">${preview.distance} Units</strong>
            </div>
            <div class="col-md-3">
              <span class="text-muted">Est. Fuel Required</span><br>
              <strong class="text-warning">${preview.required_fuel} L</strong>
            </div>
            <div class="col-md-3">
              <span class="text-muted">Current Fuel</span><br>
              <strong class="${preview.has_sufficient_fuel ? 'text-success' : 'text-danger'}">${preview.current_fuel} L (${preview.has_sufficient_fuel ? 'Sufficient' : 'Insufficient!'})</strong>
            </div>
          </div>
        `;
      }
    } catch (err) {}
  }

  if (routeShipSelect) routeShipSelect.addEventListener("change", updatePreview);
  if (routeDestSelect) routeDestSelect.addEventListener("change", updatePreview);

  if (routeForm) {
    routeForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const body = {
        ship_id: parseInt(routeShipSelect.value),
        destination_port_id: parseInt(routeDestSelect.value)
      };

      try {
        await API.post("/routes", body);
        App.showToast("Route dispatched! Ship is now in transit.", "success");
        routeForm.reset();
        document.getElementById("routePreviewBox").innerHTML = `<p class="text-muted m-0">Select a ship and destination port to preview route calculations.</p>`;
        loadRoutesAndDropdowns();
      } catch (err) {}
    });
  }

  await loadRoutesAndDropdowns();
});
