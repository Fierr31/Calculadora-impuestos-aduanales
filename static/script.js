const input = document.getElementById("productoInput");
const lista = document.getElementById("sugerencias");

let timeout = null;



input.addEventListener("input", () => {
    const valor = input.value.trim();

    // Limpiar sugerencias si está vacío
    if (valor.length === 0) {
        lista.innerHTML = "";
        return;
    }

    // Debounce: espera 300ms antes de consultar
    clearTimeout(timeout);
    timeout = setTimeout(() => {
        fetch(`http://localhost:8000/autocomplete?q=${encodeURIComponent(valor)}`)
            .then(response => response.json())
            .then(data => {
                lista.innerHTML = "";

                data.resultados.forEach(item => {
                    const li = document.createElement("li");
                    li.textContent = item.descripcion;

                    // Guardamos el id como atributo oculto
                    li.dataset.id = item.id;

                    li.addEventListener("click", () => {
                        input.value = item.descripcion;
                        lista.innerHTML = "";

                        obtenerProducto(item.id);
                    });

                    lista.appendChild(li);
                });
            });
    }, 600);
});

function obtenerProducto(id) {
    fetch(`http://localhost:8000/producto/${id}`)
        .then(response => response.json())
        .then(data => {
            mostrarResultado(data);
        });
}
