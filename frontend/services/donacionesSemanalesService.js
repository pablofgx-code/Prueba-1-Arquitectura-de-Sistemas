import { apiRequest } from "./api.js";

const BASE = "/api/donaciones";

export const donacionesService = {
  crearMes: (year, mes) =>
    apiRequest("POST", `${BASE}/`, { year, mes }),

  obtenerMes: (year, mes) =>
    apiRequest("GET", `${BASE}/${year}/${mes}`),

  obtenerTotales: (year, mes) =>
    apiRequest("GET", `${BASE}/${year}/${mes}/totales`),

registrarDonacion: (year, mes, { numero_semana, tipo_alimento, cantidad }) =>
    apiRequest("PUT", `${BASE}/${year}/${mes}`, { numero_semana, tipo_alimento, cantidad }),

  agregarSemana: (year, mes) =>
    apiRequest("POST", `${BASE}/${year}/${mes}/semanas`),

  // Ojo: este endpoint usa "semana" en singular
  eliminarSemana: (year, mes, numeroSemana) =>
    apiRequest("DELETE", `${BASE}/${year}/${mes}/semana/${numeroSemana}`),

  eliminarDonacion: (year, mes, numeroSemana, donacionId) =>
    apiRequest("DELETE", `${BASE}/${year}/${mes}/semanas/${numeroSemana}/donaciones/${encodeURIComponent(donacionId)}`),

  vaciarSemana: (year, mes, numeroSemana) =>
    apiRequest("DELETE", `${BASE}/${year}/${mes}/semanas/${numeroSemana}/donaciones`),

  modificarFecha: (year, mes, nueva_fecha) =>
    apiRequest("PATCH", `${BASE}/${year}/${mes}/fecha`, { nueva_fecha }),
};