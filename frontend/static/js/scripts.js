const boton = document.getElementById("boton-prueba");
const resultado = document.getElementById("resultado");

boton.addEventListener("click", () => {
    resultado.textContent = "¡JavaScript está funcionando!";
});