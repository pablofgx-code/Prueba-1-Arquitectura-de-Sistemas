import { perfilesService } from "/services/perfilesService.js";
import { formatearRut, validarRut } from "/services/rut.js";

function calcularEdad(fechaISO) {
  if (!fechaISO) return "";
  const hoy = new Date();
  const nac = new Date(fechaISO);
  let edad = hoy.getFullYear() - nac.getFullYear();
  const m = hoy.getMonth() - nac.getMonth();
  if (m < 0 || (m === 0 && hoy.getDate() < nac.getDate())) edad--;
  return edad >= 0 ? edad : "";
}

function init() {
  const form = document.getElementById("formPersona");
  const modalEl = document.getElementById("modalPersona");
  if (!form || !modalEl) return;

  const previa = bootstrap.Modal.getInstance(modalEl);
  if (previa) previa.dispose();
  const modal = new bootstrap.Modal(modalEl, { backdrop: true, keyboard: true, focus: true });

  const btnAbrir = document.getElementById("btnAbrirPersona");
  const inputRut = document.getElementById("rut");
  const inputFecha = document.getElementById("fecha_nacimiento");
  const inputEdad = document.getElementById("edad");
  const switchCalle = document.getElementById("situacion_calle");
  const wrapperMot = document.getElementById("wrapperMotivo");
  const inputMotivo = document.getElementById("motivo_situacion");
  const alerta = document.getElementById("alertaPersona");
  const alertaTxt = document.getElementById("alertaPersonaTexto");
  const errorEl = document.getElementById("errorPersona");
  const btnGuardar = form.querySelector('[type="submit"]');

  const mostrarError = (txt) => {
    errorEl.textContent = txt;
    errorEl.classList.toggle("d-none", !txt);
  };

  inputFecha.valueAsDate = new Date();
  inputEdad.value = calcularEdad(inputFecha.value);
  inputFecha.addEventListener("change", () => {
    inputEdad.value = calcularEdad(inputFecha.value);
  });

  // RUT: se formatea al salir del campo y se valida el dígito verificador
  const validarCampoRut = () => {
    inputRut.setCustomValidity(validarRut(inputRut.value) ? "" : "RUT inválido");
  };
  inputRut.addEventListener("blur", () => {
    if (inputRut.value.trim()) inputRut.value = formatearRut(inputRut.value);
    validarCampoRut();
  });
  inputRut.addEventListener("input", validarCampoRut);

  switchCalle.addEventListener("change", () => {
    if (switchCalle.checked) {
      wrapperMot.classList.remove("d-none");
    } else {
      wrapperMot.classList.add("d-none");
      inputMotivo.value = "";
    }
  });

  btnAbrir?.addEventListener("click", () => modal.show());

  modalEl.addEventListener("show.bs.modal", () => {
    form.classList.remove("was-validated");
    mostrarError("");
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    e.stopPropagation();

    inputRut.value = formatearRut(inputRut.value);
    validarCampoRut();

    if (!form.checkValidity()) {
      form.classList.add("was-validated");
      return;
    }

    const motivo = switchCalle.checked && inputMotivo.value.trim() ? inputMotivo.value.trim() : null;

    const payload = {
      nombre: document.getElementById("nombre").value.trim(),
      apellido: document.getElementById("apellido").value.trim(),
      rut: inputRut.value,
      contacto: document.getElementById("contacto").value.trim() || null,
      fecha_nacimiento: inputFecha.value,
      edad: parseInt(inputEdad.value, 10) || 0,
      situacion_calle: switchCalle.checked,
      motivo_situacion: motivo,
    };

    btnGuardar.disabled = true;
    mostrarError("");

    try {
      await perfilesService.registrar(payload);

      if (alerta && alertaTxt) {
        alertaTxt.textContent = `Persona "${payload.nombre} ${payload.apellido}" añadida correctamente.`;
        alerta.classList.remove("d-none");
        alerta.classList.add("show");
      }

      form.reset();
      form.classList.remove("was-validated");
      inputFecha.valueAsDate = new Date();
      inputEdad.value = calcularEdad(inputFecha.value);
      wrapperMot.classList.add("d-none");
      modal.hide();

      // Avisa a la página para que refresque sus contadores
      document.dispatchEvent(new CustomEvent("persona-creada"));
    } catch (err) {
      mostrarError(err.message || "No se pudo guardar la persona");
    } finally {
      btnGuardar.disabled = false;
    }
  });
}

init();