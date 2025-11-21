document.addEventListener('DOMContentLoaded', function() {
    const tipoProcedimientoSelect = document.getElementById('id_tipo_procedimiento');
    const tipoCirugiaDiv = document.getElementById('div_id_tipo_cirugia');

    if (tipoProcedimientoSelect && tipoCirugiaDiv) {
        function toggleTipoCirugia() {
            if (tipoProcedimientoSelect.value === 'Cirugía') {
                tipoCirugiaDiv.style.display = 'block';
            } else {
                tipoCirugiaDiv.style.display = 'none';
            }
        }
        toggleTipoCirugia();
        tipoProcedimientoSelect.addEventListener('change', toggleTipoCirugia);
    }
});