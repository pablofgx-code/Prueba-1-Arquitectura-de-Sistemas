const BASE_URL = ""; // vacío si frontend y API comparten origen

export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

function extraerMensaje(data) {
  const detail = data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((e) => e.msg).join(" · "); // 422
  return "Error inesperado del servidor";
}

export async function apiRequest(method, path, body) {
  let resp;
  try {
    resp = await fetch(`${BASE_URL}${path}`, {
      method,
      credentials: "include",
      headers: body ? { "Content-Type": "application/json" } : {},
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError(0, "No se pudo conectar con el servidor");
  }

  const data = await resp.json().catch(() => null);

  if (!resp.ok) {
    // sesión expirada: volver al login (excepto en el propio login/logout)
    if (resp.status === 401 && !path.endsWith("/login") && !path.endsWith("/logout")) {
      window.location.href = "/";
    }
    throw new ApiError(resp.status, extraerMensaje(data));
  }
  return data;
}