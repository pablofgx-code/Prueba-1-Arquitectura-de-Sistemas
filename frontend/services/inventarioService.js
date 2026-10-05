import { apiRequest } from "./api.js";

export const inventarioService = {
  listarLotes: () => apiRequest("GET", "/api/inventario/"),
};