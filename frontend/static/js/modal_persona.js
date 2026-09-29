/* =========================================================
   Lógica del modal "Añadir Persona"
   - Cálculo automático de edad
   - Toggle del campo motivo_situacion
   - Construcción del payload según el Documento Perfil
   - Inicialización segura (sin getOrCreateInstance)
   ========================================================= */
(function () {
  'use strict';

  let totalPersonas = 1248;
  let inicializado = false;

  const fmt = (n) => n.toLocaleString('es-ES');

  function actualizarContadorPersonas() {
    const el = document.getElementById('contadorPersonas');
    if (el) el.textContent = fmt(totalPersonas);
  }

  function calcularEdad(fechaISO) {
    if (!fechaISO) return '';
    const hoy = new Date();
    const nac = new Date(fechaISO);
    let edad = hoy.getFullYear() - nac.getFullYear();
    const m = hoy.getMonth() - nac.getMonth();
    if (m < 0 || (m === 0 && hoy.getDate() < nac.getDate())) edad--;
    return edad >= 0 ? edad : '';
  }

  function init() {
    if (inicializado) return;

    const form    = document.getElementById('formPersona');
    const modalEl = document.getElementById('modalPersona');

    if (!form || !modalEl) {
      console.warn('[modal_persona] No se encontró #formPersona / #modalPersona.');
      return;
    }

    inicializado = true;

    /* Limpia cualquier instancia previa corrupta y crea una nueva con config explícita */
    const previa = bootstrap.Modal.getInstance(modalEl);
    if (previa) previa.dispose();

    const modal = new bootstrap.Modal(modalEl, {
      backdrop: true,
      keyboard: true,
      focus:    true
    });

    const btnAbrir    = document.getElementById('btnAbrirPersona');
    const inputFecha  = document.getElementById('fecha_nacimiento');
    const inputEdad   = document.getElementById('edad');
    const switchCalle = document.getElementById('situacion_calle');
    const wrapperMot  = document.getElementById('wrapperMotivo');
    const inputMotivo = document.getElementById('motivo_situacion');
    const alerta      = document.getElementById('alertaPersona');
    const alertaTxt   = document.getElementById('alertaPersonaTexto');

    /* Fecha por defecto = hoy */
    inputFecha.valueAsDate = new Date();
    inputEdad.value = calcularEdad(inputFecha.value);

    /* Cálculo automático de edad */
    inputFecha.addEventListener('change', () => {
      inputEdad.value = calcularEdad(inputFecha.value);
    });

    /* Toggle del motivo según situación de calle */
    switchCalle.addEventListener('change', () => {
      if (switchCalle.checked) {
        wrapperMot.classList.remove('d-none');
      } else {
        wrapperMot.classList.add('d-none');
        inputMotivo.value = '';
      }
    });

    /* Abrir modal desde el botón (sin data-bs-toggle) */
    if (btnAbrir) {
      btnAbrir.addEventListener('click', () => modal.show());
    }

    /* Reset de validación al abrir */
    modalEl.addEventListener('show.bs.modal', () => {
      form.classList.remove('was-validated');
    });

    /* Envío */
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      e.stopPropagation();

      if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return;
      }

      const situacionCalle = switchCalle.checked;
      const motivo = situacionCalle && inputMotivo.value.trim()
        ? inputMotivo.value.trim()
        : null;

      const payload = {
        nombre:            document.getElementById('nombre').value.trim(),
        apellido:          document.getElementById('apellido').value.trim(),
        rut:               document.getElementById('rut').value.trim(),
        contacto:          document.getElementById('contacto').value.trim() || null,
        fecha_nacimiento:  inputFecha.value,
        edad:              parseInt(inputEdad.value, 10) || 0,
        situacion_calle:   situacionCalle,
        motivo_situacion:  motivo
      };

      try {
        const res = await fetch('/api/perfiles/registrar', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (!res.ok) {
          alert(data.detail || 'Error al registrar la persona');
          return;
        }

        totalPersonas += 1;
        actualizarContadorPersonas();

        if (alerta && alertaTxt) {
          alertaTxt.textContent =
            `Persona "${payload.nombre} ${payload.apellido}" añadida correctamente.`;
          alerta.classList.remove('d-none');
          alerta.classList.add('show');
        }

        form.reset();
        form.classList.remove('was-validated');
        inputFecha.valueAsDate = new Date();
        inputEdad.value = calcularEdad(inputFecha.value);
        wrapperMot.classList.add('d-none');
        modal.hide();
      } catch (err) {
        console.error('Error al guardar perfil:', err);
      }
    });

    actualizarContadorPersonas();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();