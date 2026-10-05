function mostrarAlerta(contenedor, mensaje, tipo) {
  if (!contenedor) return;
  const div = document.createElement("div");
  div.className = `alert alert-${tipo}`;
  div.setAttribute("role", "alert");
  div.textContent = mensaje;
  contenedor.replaceChildren(div);
}

export function bindForm(form, handler) {
  const salida = document.querySelector(form.dataset.target);
  const boton = form.querySelector('[type="submit"]');

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    boton.disabled = true;
    salida?.replaceChildren();

    try {
      const datos = Object.fromEntries(new FormData(form));
      const resultado = await handler(datos, form);
      if (resultado?.mensaje) mostrarAlerta(salida, resultado.mensaje, "success");
    } catch (err) {
      mostrarAlerta(salida, err.message || "Error inesperado", "danger");
    } finally {
      boton.disabled = false;
    }
  });
}