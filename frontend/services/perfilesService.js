import { apiRequest, ApiError } from "./api.js";

const BASE = "/api/perfiles";

export const perfilesService = {
  registrar: (perfil) => apiRequest("POST", `${BASE}/registrar`, perfil),

  listar: () => apiRequest("GET", `${BASE}/listar`),

  obtenerPorRut: (rut) => apiRequest("GET", `${BASE}/${encodeURIComponent(rut)}`),

  eliminar: (rut) => apiRequest("DELETE", `${BASE}/${encodeURIComponent(rut)}`),

registrarRetiro: (rut) =>
    apiRequest("POST", `${BASE}/${encodeURIComponent(rut)}/retiros`),
  resumenRetiros: (year) => apiRequest("GET", `${BASE}/resumen/retiros/${year}`),

  // Devuelve un archivo, no JSON, así que no pasa por apiRequest
  async descargarExcel() {
    let resp;
    try {
      resp = await fetch(`${BASE}/reporte/excel`, { credentials: "include" });
    } catch {
      throw new ApiError(0, "No se pudo conectar con el servidor");
    }
    if (resp.status === 401) {
      window.location.href = "/login";
      throw new ApiError(401, "Sesión expirada");
    }
    if (!resp.ok) throw new ApiError(resp.status, "No se pudo generar el reporte");

    const url = URL.createObjectURL(await resp.blob());
    const a = document.createElement("a");
    a.href = url;
    a.download = `retiros_donaciones_${new Date().getFullYear()}.xlsx`;
    a.click();
    URL.revokeObjectURL(url);
  },
};