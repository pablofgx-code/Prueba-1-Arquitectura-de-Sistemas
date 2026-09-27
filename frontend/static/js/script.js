// Código de prueba anterior, protegido por si el elemento no existe en esta página
const boton = document.getElementById("boton-prueba");
const resultado = document.getElementById("resultado");
if (boton && resultado) {
  boton.addEventListener("click", () => {
    resultado.textContent = "¡JavaScript está funcionando!";
  });
}

// Manejo de la respuesta del login
document.body.addEventListener("htmx:afterRequest", function (evt) {
  if (evt.target.id !== "login-form") return;

  const responseDiv = document.getElementById("login-response");
  let data = {};
  try {
    data = JSON.parse(evt.detail.xhr.responseText);
  } catch (e) {
    data = { detail: "Ocurrió un error inesperado. Intenta nuevamente." };
  }

  if (evt.detail.successful) {
    responseDiv.innerHTML = `<div class="alert alert-success">${data.mensaje ?? "Inicio de sesión exitoso"}</div>`;
    const homeUrl = evt.target.dataset.homeUrl || "/";
    setTimeout(() => { window.location.href = homeUrl; }, 500);
  } else {
    const mensaje = data.detail || "Correo o contraseña incorrectos.";
    responseDiv.innerHTML = `<div class="alert alert-danger">${mensaje}</div>`;
  }
});