document.addEventListener("DOMContentLoaded", async () => {
  Auth.requireAuth();

  let fuelChart = null;

  async function loadReportsPage() {
    try {
      const analytics = await API.get("/reports/analytics");
      const fuelLogs = await API.get("/reports/fuel-logs");
      const movements = await API.get("/reports/movement-history");

      // Fuel consumption chart
      const ctx = document.getElementById("fuelReportChart");
      if (ctx) {
        const labels = fuelLogs.slice(0, 10).reverse().map(l => l.timestamp);
        const amounts = fuelLogs.slice(0, 10).reverse().map(l => l.amount);

        if (fuelChart) fuelChart.destroy();
        fuelChart = new Chart(ctx, {
          type: 'line',
          data: {
            labels: labels,
            datasets: [{
              label: 'Fuel Activity (L)',
              data: amounts,
              borderColor: '#f59e0b',
              backgroundColor: 'rgba(245, 158, 11, 0.1)',
              fill: true,
              tension: 0.3
            }]
          },
          options: { responsive: true }
        });
      }

      // Movement logs table
      const movementBody = document.getElementById("fullMovementTableBody");
      if (movementBody) {
        movementBody.innerHTML = movements.map(m => `
          <tr>
            <td>#${m.id}</td>
            <td><strong>${m.ship_name}</strong></td>
            <td>${m.origin_port} &rarr; ${m.destination_port}</td>
            <td>${m.details}</td>
            <td>${m.timestamp}</td>
          </tr>
        `).join("");
      }

      // Fuel logs table
      const fuelBody = document.getElementById("fullFuelTableBody");
      if (fuelBody) {
        fuelBody.innerHTML = fuelLogs.map(l => `
          <tr>
            <td>#${l.id}</td>
            <td><strong>${l.ship_name}</strong></td>
            <td><span class="badge bg-${l.action.includes('Refuel') ? 'success' : 'warning'}">${l.action}</span></td>
            <td>${l.amount} L</td>
            <td>${l.fuel_before} L &rarr; ${l.fuel_after} L</td>
            <td>${l.timestamp}</td>
          </tr>
        `).join("");
      }

    } catch (err) {
      console.error("Load reports error:", err);
    }
  }

  window.downloadCSV = (type) => {
    window.location.href = `${CONFIG.API_BASE_URL}/reports/export/csv?type=${type}`;
  };

  await loadReportsPage();
});
