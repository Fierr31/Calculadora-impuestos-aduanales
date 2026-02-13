const productoInput = document.getElementById("productoInput");
const sugerencias = document.getElementById("sugerencias");
const detalleContenedor = document.getElementById("productoDetalleContenido");

let debounceTimer;
let productoSeleccionado = null;

function limpiarSugerencias() {
  sugerencias.innerHTML = "";
  sugerencias.style.display = "none";
}

function renderSugerencias(productos) {
  if (!productos.length) {
    sugerencias.innerHTML = '<div class="sugerencia-item vacio">Sin resultados</div>';
    sugerencias.style.display = "block";
    return;
  }

  sugerencias.innerHTML = productos
    .map(
      (producto) =>
        `<button class="sugerencia-item" data-id="${producto.id}" data-name="${producto.nombre}">
          <strong>${producto.nombre}</strong>
          <small>${producto.categoria || "Sin categoría"}</small>
        </button>`
    )
    .join("");

  sugerencias.style.display = "block";
}

async function buscarProductos(query) {
  try {
    const response = await fetch(`/api/productos?query=${encodeURIComponent(query)}`);
    if (!response.ok) {
      throw new Error("Error al buscar productos");
    }

    const productos = await response.json();
    renderSugerencias(productos);
  } catch (error) {
    sugerencias.innerHTML = `<div class="sugerencia-item vacio">${error.message}</div>`;
    sugerencias.style.display = "block";
  }
}

function renderDetalle(producto) {
  const requisitos = (producto.requisitos || []).length
    ? `<ul>${producto.requisitos.map((req) => `<li>${req}</li>`).join("")}</ul>`
    : "No hay requisitos adicionales.";

  detalleContenedor.innerHTML = `
    <div class="detalle-grid">
      <p><strong>Nombre:</strong> ${producto.nombre}</p>
      <p><strong>Categoría:</strong> ${producto.categoria || "N/A"}</p>
      <p><strong>Descripción:</strong> ${producto.descripcion || "N/A"}</p>
      <p><strong>Precio referencia:</strong> ${producto.precio_referencia ?? "N/A"}</p>
      <p><strong>Arancel:</strong> ${producto.arancel ?? "N/A"}%</p>
      <p><strong>País sugerido:</strong> ${producto.pais_origen_sugerido || "N/A"}</p>
      <div><strong>Requisitos:</strong> ${requisitos}</div>
    </div>
  `;
}

async function cargarDetalleProducto(productoId) {
  try {
    const response = await fetch(`/api/productos/${productoId}`);
    if (!response.ok) {
      throw new Error("No se pudo cargar el detalle");
    }

    const producto = await response.json();
    renderDetalle(producto);
  } catch (error) {
    detalleContenedor.textContent = error.message;
  }
}

productoInput.addEventListener("input", (event) => {
  const query = event.target.value.trim();
  productoSeleccionado = null;

  if (query.length < 2) {
    limpiarSugerencias();
    return;
  }

  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => buscarProductos(query), 250);
});

sugerencias.addEventListener("click", (event) => {
  const option = event.target.closest(".sugerencia-item");
  if (!option || !option.dataset.id) {
    return;
  }

  productoSeleccionado = option.dataset.id;
  productoInput.value = option.dataset.name;
  limpiarSugerencias();
  cargarDetalleProducto(productoSeleccionado);
});

document.addEventListener("click", (event) => {
  if (!event.target.closest(".autocomplete-container")) {
    limpiarSugerencias();
  }
});
