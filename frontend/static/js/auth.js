import { authService } from "/services/authService.js";
import { bindForm } from "./forms.js";

const handlers = {
  login: async (datos, form) => {
    await authService.login(datos);
    window.location.href = form.dataset.homeUrl;
  },

  "cambiar-password": async (datos, form) => {
    const res = await authService.cambiarPassword(datos);
    form.reset();
    return res;
  },
};

document.querySelectorAll("form[data-form]").forEach((form) => {
  const handler = handlers[form.dataset.form];
  if (handler) bindForm(form, handler);
});

document.addEventListener("click", async (e) => {
  const boton = e.target.closest("[data-logout]");
  if (!boton) return;

  e.preventDefault();
  boton.disabled = true;
  const loginUrl = boton.dataset.loginUrl;

  try {
    await authService.logout();
  } catch {
    /* aunque falle, vamos al login */
  }
  window.location.href = loginUrl;
});