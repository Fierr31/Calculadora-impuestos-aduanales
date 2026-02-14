const input = document.getElementById("productoInput");
const lista = document.getElementById("sugerencias");

let timeout = null;

const etiquetas = {
    fraccion: "Fracción",
    descripcion: "Descripción",
    unidad_medida: "Unidad de Medida",
    impuesto: "Impuesto (%)"
};


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
            console.log("Respuesta backend:", data);
            mostrarResultado(data);
        });
}


function mostrarResultado(data) {
    const contenedor = document.getElementById("resultadoContenido");

    if (!data || Object.keys(data).length === 0) {
        contenedor.innerHTML = "<p>No se encontró información.</p>";
        return;
    }

    const tabla = document.createElement("table");

    for (const clave in data) {

        if (clave === "id" || clave === "exento") continue;

        const fila = document.createElement("tr");

        const celdaClave = document.createElement("td");
        celdaClave.textContent = etiquetas[clave] || clave;

        const celdaValor = document.createElement("td");
        celdaValor.textContent = data[clave];

        fila.appendChild(celdaClave);
        fila.appendChild(celdaValor);
        tabla.appendChild(fila);
    }

    contenedor.innerHTML = "";
    contenedor.appendChild(tabla);

    procesarDatos(data);
}

function procesarDatos(datos) {
    console.log("Procesando:", datos);
    // Aquí haces cálculos de impuestos, totales, etc.
}