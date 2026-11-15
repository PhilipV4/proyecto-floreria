const inputFecha = document.getElementById('id_fecha_entrega');
if (inputFecha) {
    // Calculamos el día de mañana
    const manana = new Date();
    manana.setDate(manana.getDate() + 1);

    flatpickr(inputFecha, {
        locale: "es",
        minDate: manana,          // 👈 Bloquea hoy y días pasados, permitiendo desde mañana
        dateFormat: "Y-m-d",
        altInput: true,
        altFormat: "d/m/Y",
        allowInput: false,
        disableMobile: true
    });
}