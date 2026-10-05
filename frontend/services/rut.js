// Cambia a false si en tu base los RUT están guardados sin puntos (12345678-9)
const CON_PUNTOS = true;

export const limpiarRut = (s) => String(s ?? "").replace(/[^0-9kK]/g, "").toUpperCase();

export function formatearRut(s) {
  const c = limpiarRut(s);
  if (c.length < 2) return String(s ?? "").trim();
  const cuerpo = c.slice(0, -1);
  const dv = c.slice(-1);
  const conPuntos = CON_PUNTOS ? cuerpo.replace(/\B(?=(\d{3})+(?!\d))/g, ".") : cuerpo;
  return `${conPuntos}-${dv}`;
}

export function validarRut(s) {
  const c = limpiarRut(s);
  const cuerpo = c.slice(0, -1);
  const dv = c.slice(-1);
  if (!/^\d{7,8}$/.test(cuerpo)) return false;

  let suma = 0, mult = 2;
  for (let i = cuerpo.length - 1; i >= 0; i--) {
    suma += Number(cuerpo[i]) * mult;
    mult = mult === 7 ? 2 : mult + 1;
  }
  const r = 11 - (suma % 11);
  const esperado = r === 11 ? "0" : r === 10 ? "K" : String(r);
  return dv === esperado;
}