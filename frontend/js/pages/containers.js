document.addEventListener("DOMContentLoaded", async () => {
  Auth.requireAuth();

  const searchInput = document.getElementById("searchContainerInput");
  const typeFilter = document.getElementById("filterTypeSelect");
  const containersTableBody = document.getElementById("containersTableBody");
  const containerForm = document.getElementById("containerForm");
  const loadUnloadForm = document.getElementById("loadUnloadForm");

  async function loadContainers() {
    try {
      const search = searchInput ? searchInput.value.trim() : "";
      const type = typeFilter ? typeFilter.value : "";
      const containers = await API.get(`/containers?search=${encodeURIComponent(search)}&type_filter=${encodeURIComponent(type)}`);
      const ports = await API.get("/ports");
      const ships = await API.get("/ships");

      const portMap = {}; ports.forEach(p => portMap[p.id] = p.name);
      const shipMap = {}; ships.forEach(s => shipMap[s.id] = s.name);

      if (containersTableBody) {
        containersTableBody.innerHTML = containers.map(c => `
          <tr>
            <td><strong>${c.container_code}</strong></td>
            <td><span class="badge bg-${c.type === 'Heavy' ? 'danger' : (c.type === 'Refrigerated' ? 'info' : (c.type === 'Liquid' ? 'warning' : 'primary'))}">${c.type}</span></td>
            <td>${c.weight} Tons</td>
            <td><span class="badge bg-secondary">${c.status}</span></td>
            <td>${c.current_port_id ? portMap[c.current_port_id] || 'Port ' + c.current_port_id : '-'}</td>
            <td>${c.assigned_ship_id ? shipMap[c.assigned_ship_id] || 'Ship ' + c.assigned_ship_id : '-'}</td>
            <td>
              ${Auth.hasRole("Administrator", "Port Manager") ? `
                ${c.current_port_id ? `<button class="btn btn-sm btn-outline-primary" onclick="openLoadModal(${c.id}, '${c.container_code}', ${c.current_port_id})"><i class="bi bi-box-arrow-in-right"></i> Load on Ship</button>` : ''}
                ${c.assigned_ship_id ? `<button class="btn btn-sm btn-outline-success" onclick="openUnloadModal(${c.id}, '${c.container_code}', ${c.assigned_ship_id})"><i class="bi bi-box-arrow-left"></i> Unload to Port</button>` : ''}
                <button class="btn btn-sm btn-outline-danger" onclick="deleteContainer(${c.id})"><i class="bi bi-trash"></i></button>
              ` : ''}
            </td>
          </tr>
        `).join("");
      }

      // Update dropdown options
      const containerPortSel = document.getElementById("containerPort");
      if (containerPortSel) {
        containerPortSel.innerHTML = `<option value="">None (On Ship)</option>` + ports.map(p => `<option value="${p.id}">${p.name}</option>`).join("");
      }

    } catch (err) {
      console.error("Load containers error:", err);
    }
  }

  if (searchInput) searchInput.addEventListener("input", loadContainers);
  if (typeFilter) typeFilter.addEventListener("change", loadContainers);

  if (containerForm) {
    containerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const body = {
        container_code: document.getElementById("containerCode").value,
        type: document.getElementById("containerType").value,
        weight: parseFloat(document.getElementById("containerWeight").value),
        current_port_id: document.getElementById("containerPort").value ? parseInt(document.getElementById("containerPort").value) : null
      };

      try {
        await API.post("/containers", body);
        App.showToast("Container added successfully", "success");
        const modal = bootstrap.Modal.getInstance(document.getElementById("containerModal"));
        if (modal) modal.hide();
        loadContainers();
      } catch (err) {}
    });
  }

  window.openLoadModal = async (containerId, code, currentPortId) => {
    const ships = await API.get("/ships");
    const dockedShips = ships.filter(s => s.current_port_id === currentPortId);

    if (dockedShips.length === 0) {
      App.showToast("No ships currently docked at this port to load onto.", "warning");
      return;
    }

    const shipSelect = document.getElementById("targetShipSelect");
    shipSelect.innerHTML = dockedShips.map(s => `<option value="${s.id}">${s.name} (Cap: ${s.current_weight}/${s.max_weight} T)</option>`).join("");
    document.getElementById("loadContainerId").value = containerId;
    document.getElementById("loadContainerCode").textContent = code;
    new bootstrap.Modal(document.getElementById("loadModal")).show();
  };

  window.openUnloadModal = async (containerId, code, currentShipId) => {
    const ports = await API.get("/ports");
    const portSelect = document.getElementById("targetPortSelect");
    portSelect.innerHTML = ports.map(p => `<option value="${p.id}">${p.name} (Storage: ${p.stored_containers_count}/${p.available_storage})</option>`).join("");
    document.getElementById("unloadContainerId").value = containerId;
    document.getElementById("unloadContainerCode").textContent = code;
    new bootstrap.Modal(document.getElementById("unloadModal")).show();
  };

  const loadForm = document.getElementById("loadForm");
  if (loadForm) {
    loadForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const cid = document.getElementById("loadContainerId").value;
      const shipId = parseInt(document.getElementById("targetShipSelect").value);
      try {
        await API.post(`/containers/${cid}/load`, { ship_id: shipId });
        App.showToast("Container loaded onto ship successfully", "success");
        const modal = bootstrap.Modal.getInstance(document.getElementById("loadModal"));
        if (modal) modal.hide();
        loadContainers();
      } catch (err) {}
    });
  }

  const unloadForm = document.getElementById("unloadForm");
  if (unloadForm) {
    unloadForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const cid = document.getElementById("unloadContainerId").value;
      const portId = parseInt(document.getElementById("targetPortSelect").value);
      try {
        await API.post(`/containers/${cid}/unload`, { port_id: portId });
        App.showToast("Container unloaded to port successfully", "success");
        const modal = bootstrap.Modal.getInstance(document.getElementById("unloadModal"));
        if (modal) modal.hide();
        loadContainers();
      } catch (err) {}
    });
  }

  window.deleteContainer = async (id) => {
    if (confirm("Are you sure you want to delete this container?")) {
      try {
        await API.delete(`/containers/${id}`);
        App.showToast("Container deleted", "success");
        loadContainers();
      } catch (err) {}
    }
  };

  await loadContainers();
});
