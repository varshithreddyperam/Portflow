document.addEventListener("DOMContentLoaded", async () => {
  Auth.requireAuth();

  const searchInput = document.getElementById("searchPortInput");
  const portsGrid = document.getElementById("portsGrid");
  const portForm = document.getElementById("portForm");

  async function loadPorts() {
    try {
      const query = searchInput ? searchInput.value.trim() : "";
      const ports = await API.get(`/ports?search=${encodeURIComponent(query)}`);

      if (portsGrid) {
        portsGrid.innerHTML = ports.map(p => `
          <div class="col-md-6 col-lg-4 mb-4">
            <div class="card glass-card h-100">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <h5 class="card-title text-primary m-0"><i class="bi bi-geo-alt-fill me-2"></i>${p.name}</h5>
                  <span class="badge bg-secondary">ID: ${p.id}</span>
                </div>
                <p class="text-muted mb-2"><small>Cartesian Coords: (${p.x_coord}, ${p.y_coord})</small></p>
                <hr class="border-secondary">
                <div class="mb-2">
                  <div class="d-flex justify-content-between text-sm mb-1">
                    <span>Dock Occupancy:</span>
                    <span><strong>${p.docked_ships_count} / ${p.dock_capacity} Ships</strong></span>
                  </div>
                  <div class="progress" style="height: 8px;">
                    <div class="progress-bar bg-info" style="width: ${(p.docked_ships_count / p.dock_capacity) * 100}%"></div>
                  </div>
                </div>
                <div class="mb-3">
                  <div class="d-flex justify-content-between text-sm mb-1">
                    <span>Storage Containers:</span>
                    <span><strong>${p.stored_containers_count} / ${p.available_storage}</strong></span>
                  </div>
                  <div class="progress" style="height: 8px;">
                    <div class="progress-bar bg-success" style="width: ${(p.stored_containers_count / p.available_storage) * 100}%"></div>
                  </div>
                </div>
                <div class="d-flex justify-content-end gap-2">
                  ${Auth.hasRole("Administrator", "Port Manager") ? `
                    <button class="btn btn-sm btn-outline-warning" onclick="editPort(${p.id}, '${p.name}', ${p.x_coord}, ${p.y_coord}, ${p.dock_capacity}, ${p.available_storage})"><i class="bi bi-pencil"></i> Edit</button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deletePort(${p.id})"><i class="bi bi-trash"></i> Delete</button>
                  ` : ''}
                </div>
              </div>
            </div>
          </div>
        `).join("");
      }
    } catch (err) {
      console.error("Load ports error:", err);
    }
  }

  if (searchInput) {
    searchInput.addEventListener("input", loadPorts);
  }

  if (portForm) {
    portForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const portId = document.getElementById("portId").value;
      const body = {
        name: document.getElementById("portName").value,
        x_coord: parseFloat(document.getElementById("portX").value),
        y_coord: parseFloat(document.getElementById("portY").value),
        dock_capacity: parseInt(document.getElementById("portDockCap").value),
        available_storage: parseInt(document.getElementById("portStorageCap").value),
      };

      try {
        if (portId) {
          await API.put(`/ports/${portId}`, body);
          App.showToast("Port updated successfully", "success");
        } else {
          await API.post("/ports", body);
          App.showToast("Port created successfully", "success");
        }
        const modal = bootstrap.Modal.getInstance(document.getElementById("portModal"));
        if (modal) modal.hide();
        loadPorts();
      } catch (err) {}
    });
  }

  window.editPort = (id, name, x, y, dockCap, storageCap) => {
    document.getElementById("portId").value = id;
    document.getElementById("portName").value = name;
    document.getElementById("portX").value = x;
    document.getElementById("portY").value = y;
    document.getElementById("portDockCap").value = dockCap;
    document.getElementById("portStorageCap").value = storageCap;
    document.getElementById("portModalTitle").textContent = "Edit Port";
    new bootstrap.Modal(document.getElementById("portModal")).show();
  };

  window.deletePort = async (id) => {
    if (confirm("Are you sure you want to delete this port?")) {
      try {
        await API.delete(`/ports/${id}`);
        App.showToast("Port deleted", "success");
        loadPorts();
      } catch (err) {}
    }
  };

  window.resetPortForm = () => {
    document.getElementById("portId").value = "";
    document.getElementById("portForm").reset();
    document.getElementById("portModalTitle").textContent = "Add New Port";
  };

  await loadPorts();
});
