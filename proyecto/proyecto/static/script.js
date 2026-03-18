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