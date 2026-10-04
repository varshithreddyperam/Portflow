const isFileProtocol = window.location.protocol === "file:";

const CONFIG = {
  API_BASE_URL: isFileProtocol 
    ? "http://localhost:8000/api" 
    : window.location.origin + "/api",
  WS_URL: isFileProtocol
    ? "ws://localhost:8000/api/simulation/ws"
    : (window.location.protocol === "https:" ? "wss://" : "ws://") + window.location.host + "/api/simulation/ws"
};
