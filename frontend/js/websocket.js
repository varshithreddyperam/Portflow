const SimulationWS = {
  socket: null,
  listeners: [],

  connect: () => {
    if (SimulationWS.socket && SimulationWS.socket.readyState === WebSocket.OPEN) return;

    SimulationWS.socket = new WebSocket(CONFIG.WS_URL);

    SimulationWS.socket.onopen = () => {
      console.log("WebSocket connected to PortFlow Simulation Engine.");
    };

    SimulationWS.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "NOTIFICATION") {
          App.showToast(data.message, data.level || "info");
        }
        SimulationWS.listeners.forEach(cb => cb(data));
      } catch (err) {
        console.error("WS message parse error:", err);
      }
    };

    SimulationWS.socket.onclose = () => {
      console.warn("WS connection closed. Reconnecting in 3s...");
      setTimeout(SimulationWS.connect, 3000);
    };
  },

  subscribe: (callback) => {
    SimulationWS.listeners.push(callback);
  }
};
