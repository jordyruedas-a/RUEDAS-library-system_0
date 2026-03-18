function toggleUserForm() {
    const form = document.getElementById('user-form');
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

function toggleBookForm() {
    const form = document.getElementById('book-form');
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

function toggleSaleForm() {
    const form = document.getElementById('sale-form');
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

function confirmDelete() {
    return confirm('¿Estás seguro de eliminar este registro?');
}

// Inicialización: Ocultar todos los formularios al cargar
window.onload = function() {
    document.getElementById('user-form').style.display = 'none';
    document.getElementById('book-form').style.display = 'none';
    document.getElementById('sale-form').style.display = 'none';
};

// Validación de teléfono en tiempo real
document.querySelectorAll('input[type="text"][name="telefono"]').forEach(input => {
    input.addEventListener('input', function(e) {
        this.value = this.value.replace(/\D/g, '').slice(0, 10);
    });
});

// Validación de números
document.querySelectorAll('input[type="number"]').forEach(input => {
    input.addEventListener('input', function(e) {
        if (this.min) this.value = Math.max(parseInt(this.min), this.value);
        if (this.max) this.value = Math.min(parseInt(this.max), this.value);
    });
});





// Función para clonar el template de libros
function agregarLibro() {
    const contenedor = document.getElementById('libros-container');
    const template = contenedor.querySelector('.grupo-libro-template');
    const nuevoGrupo = template.cloneNode(true);

    nuevoGrupo.classList.remove('grupo-libro-template');
    nuevoGrupo.querySelector('.select-libro').selectedIndex = 0;
    nuevoGrupo.querySelector('.input-cantidad').value = 1;

    // Agregar eventos al nuevo grupo
    nuevoGrupo.querySelector('.select-libro').addEventListener('change', actualizarTotales);
    nuevoGrupo.querySelector('.input-cantidad').addEventListener('input', actualizarTotales);

    contenedor.appendChild(nuevoGrupo);
    actualizarTotales();
}

// Función para actualizar totales
function actualizarTotales() {
    let totalCalculado = 0;

    document.querySelectorAll('.grupo-libro:not(.grupo-libro-template)').forEach(grupo => {
        const select = grupo.querySelector('.select-libro');
        const cantidadInput = grupo.querySelector('.input-cantidad');

        if (select.value && select.selectedOptions[0].dataset.precio) {
            const precio = parseFloat(select.selectedOptions[0].dataset.precio);
            const cantidad = parseInt(cantidadInput.value) || 0;
            const stockDisponible = parseInt(select.selectedOptions[0].dataset.stock);

            // Validar stock
            if (cantidad > stockDisponible) {
                cantidadInput.setCustomValidity('Cantidad excede el stock disponible');
                cantidadInput.reportValidity();
            } else {
                cantidadInput.setCustomValidity('');
                totalCalculado += precio * cantidad;
            }
        }
    });

    document.getElementById('total').textContent = totalCalculado.toFixed(2);
    calcularCambio();
}

// Función para calcular el cambio
function calcularCambio() {
    const montoPagado = parseFloat(document.getElementById('monto-pagado').value) || 0;
    const total = parseFloat(document.getElementById('total').textContent);
    const cambio = montoPagado - total;

    document.getElementById('cambio').textContent = cambio >= 0 ? cambio.toFixed(2) : '0.00';

    // Resaltar si el pago es insuficiente
    if (cambio < 0) {
        document.getElementById('cambio').style.color = '#e74c3c';
    } else {
        document.getElementById('cambio').style.color = '#27ae60';
    }
}

// Función para eliminar libro
function eliminarLibro(boton) {
    const grupo = boton.closest('.grupo-libro');
    if (document.querySelectorAll('.grupo-libro').length > 1) {
        grupo.parentElement.remove();
        actualizarTotales();
    }
}

// Eventos iniciales
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('monto-pagado').addEventListener('input', calcularCambio);

    document.querySelectorAll('.select-libro, .input-cantidad').forEach(elemento => {
        elemento.addEventListener('change', actualizarTotales);
        elemento.addEventListener('input', actualizarTotales);
    });

    document.getElementById('formVenta').addEventListener('submit', function(e) {
        const total = parseFloat(document.getElementById('total').textContent);
        const montoPagado = parseFloat(document.getElementById('monto-pagado').value);

        if (montoPagado < total) {
            e.preventDefault();
            alert('El monto pagado no cubre el total de la compra');
        }
    });
});

// Validación de año
document.querySelectorAll('input[name="anio"]').forEach(input => {
    input.addEventListener('input', function(e) {
        this.value = this.value.replace(/\D/g, '').slice(0, 4);
    });
});