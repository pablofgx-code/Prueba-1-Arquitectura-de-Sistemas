import { apiRequest } from "./api.js";

export const homeService = {
  obtenerDashboard: () => apiRequest("GET", "/api/metricas/dashboard"),
};