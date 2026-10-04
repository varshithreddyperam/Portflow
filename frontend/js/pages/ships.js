document.addEventListener("DOMContentLoaded", async () => {
  Auth.requireAuth();

  const searchInput = document.getElementById("searchShipInput");
  const shipsTableBody = document.getElementById("shipsTableBody");
  const shipForm = document.getElementById("shipForm");
  const refuelForm = document.getElementById("refuelForm");

  async function loadShips() {
    try {
      const query = searchInput ? searchInput.value.trim() : "";
      const ships = await API.get(`/ships?search=${encodeURIComponent(query)}`);
      const ports = await API.get("/ports");
      const portMap = {};
      ports.forEach(p => portMap[p.id] = p.name);

      if (shipsTableBody) {
        shipsTableBody.innerHTML = ships.map(s => `
          <tr>
            <td><strong>${s.name}</strong> <small class="text-muted">(ID: ${s.id})</small></td>
            <td>
              <span class="badge badge-status ${s.status === 'Docked' ? 'badge-docked' : (s.status === 'In Transit' ? 'badge-transit' : 'badge-maintenance')}">
                ${s.status}
              </span>
            </td>
            <td>${s.current_port_id ? portMap[s.current_port_id] || 'Port ' + s.current_port_id : '<span class="text-info"><i class="bi bi-water"></i> In Transit</span>'}</td>
            <td>
              <div class="d-flex align-items-center">
                <div class="progress flex-grow-1 me-2" style="height: 10px;">
                  <div class="progress-bar bg-${s.current_fuel < (s.fuel_capacity * 0.2) ? 'danger' : 'warning'}" style="width: ${(s.current_fuel / s.fuel_capacity) * 100}%"></div>
                </div>
                <small>${s.current_fuel} / ${s.fuel_capacity} L</small>
              </div>
            </td>
            <td>
              <small>
                Total Weight: <strong>${s.current_weight} / ${s.max_weight} T</strong><br>
                Heavy: ${s.heavy_count}/${s.heavy_limit} | Refrig: ${s.refrigerated_count}/${s.refrigerated_limit} | Liquid: ${s.liquid_count}/${s.liquid_limit}
              </small>
            </td>
            <td>
              ${Auth.hasRole("Administrator", "Fleet Manager") ? `
                <button class="btn btn-sm btn-outline-success" onclick="openRefuelModal(${s.id}, '${s.name}', ${s.current_fuel}, ${s.fuel_capacity})"><i class="bi bi-fuel-pump"></i> Refuel</button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteShip(${s.id})"><i class="bi bi-trash"></i></button>
              ` : ''}
            </td>
          </tr>
        `).join("");
      }

      // Populate ports dropdown in ship form
      const shipPortSelect = document.getElementById("shipCurrentPort");
      if (shipPortSelect) {
        shipPortSelect.innerHTML = `<option value="">In Transit / Off-Dock</option>` + ports.map(p => `<option value="${p.id}">${p.name}</option>`).join("");
      }

    } catch (err) {
      console.error("Load ships error:", err);
    }
  }

  if (searchInput) searchInput.addEventListener("input", loadShips);

  if (shipForm) {
    shipForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const body = {
        name: document.getElementById("shipName").value,
        max_weight: parseFloat(document.getElementById("shipMaxWeight").value),
        fuel_capacity: parseFloat(document.getElementById("shipFuelCapacity").value),
        heavy_limit: parseInt(document.getElementById("shipHeavyLimit").value),
        refrigerated_limit: parseInt(document.getElementById("shipRefrigLimit").value),
        liquid_limit: parseInt(document.getElementById("shipLiquidLimit").value),
        current_port_id: document.getElementById("shipCurrentPort").value ? parseInt(document.getElementById("shipCurrentPort").value) : null
      };

      try {
        await API.post("/ships", body);
        App.showToast("Ship created successfully", "success");
        const modal = bootstrap.Modal.getInstance(document.getElementById("shipModal"));
        if (modal) modal.hide();
        loadShips();
      } catch (err) {}
    });
  }

  if (refuelForm) {
    refuelForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const shipId = document.getElementById("refuelShipId").value;
      const amount = parseFloat(document.getElementById("refuelAmount").value);
      try {
        await API.post(`/ships/${shipId}/refuel`, { amount });
        App.showToast("Ship refueled successfully", "success");
        const modal = bootstrap.Modal.getInstance(document.getElementById("refuelModal"));
        if (modal) modal.hide();
        loadShips();
      } catch (err) {}
    });
  }

  window.openRefuelModal = (id, name, currentFuel, capacity) => {
    document.getElementById("refuelShipId").value = id;
    document.getElementById("refuelShipName").textContent = name;
    document.getElementById("refuelFuelInfo").textContent = `${currentFuel} / ${capacity} L`;
    new bootstrap.Modal(document.getElementById("refuelModal")).show();
  };

  window.deleteShip = async (id) => {
    if (confirm("Are you sure you want to delete this ship?")) {
      try {
        await API.delete(`/ships/${id}`);
        App.showToast("Ship deleted", "success");
        loadShips();
      } catch (err) {}
    }
  };

  await loadShips();
});
