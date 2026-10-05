import { apiRequest } from "./api.js";

const PREFIX = "/api/auth";

export const authService = {
  login: ({ email, password }) =>
    apiRequest("POST", `${PREFIX}/login`, { email, password }),

  logout: () => apiRequest("POST", `${PREFIX}/logout`),

  cambiarPassword: ({ password_actual, nueva_password }) =>
    apiRequest("PUT", `${PREFIX}/cambiar-password`, { password_actual, nueva_password }),
};