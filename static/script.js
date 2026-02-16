const input = document.getElementById("productoInput");
const lista = document.getElementById("sugerencias");
let productoSeleccionado = null;

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
    productoSeleccionado = data;  // guardamos el objeto completo

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
}


function procesarDatos(datos) {
    console.log("Procesando:", datos);
}

document.getElementById("calcularBtn").addEventListener("click", async () => {

    if (!productoSeleccionado) {
        alert("Selecciona un producto primero");
        return;
    }

    const precio = parseFloat(document.getElementById("preciounit").value);
    const cantidad = parseInt(document.getElementById("cantidad").value);
    const pais = document.getElementById("pais").value.toLowerCase();
    const flete = parseFloat(document.getElementById("flete").value);
    const seguro = parseFloat(document.getElementById("seguro").value);

    if (isNaN(precio) || isNaN(cantidad) || isNaN(flete) || isNaN(seguro)) {
    alert("Completa todos los campos");
    return;
}


    const response = await fetch("http://localhost:8000/calcular", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            precio,
            cantidad,
            pais,
            flete,
            seguro,
            impuesto: productoSeleccionado.impuesto,
            fracc: productoSeleccionado.fraccion
        })
    });

    const data = await response.json();

    if (!response.ok) {
        alert(data.detail || "Error en el cálculo");
        return;
    }

    if (data.status === "prohibido") {
        alert(data.mensaje);
        document.getElementById("baseg").style.display = "none";
        return;
    }

    document.getElementById("va").textContent = data.valor_en_aduana.toFixed(2);
    document.getElementById("igi").textContent = data.igi.toFixed(2);
    document.getElementById("dta").textContent = data.dta.toFixed(2);
    document.getElementById("base").textContent = data.base_gravable.toFixed(2);
    document.getElementById("ieps").textContent = data.ieps.toFixed(2);
    document.getElementById("total").textContent = data.total.toFixed(2);
    document.getElementById("iva").textContent = data.iva.toFixed(2);

    document.getElementById("baseg").style.display = "block";
});
