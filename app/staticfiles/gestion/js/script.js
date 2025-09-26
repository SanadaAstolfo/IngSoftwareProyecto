document.addEventListener('DOMContentLoaded', function() {
    const diagnosticoSelect = document.getElementById('id_diagnostico_opciones');
    const diagnosticoTextoInput = document.getElementById('id_diagnostico_personalizado');

    if (!diagnosticoSelect || !diagnosticoTextoInput) return;

    function toggleOtroDiagnostico() {
        const selectedOptionText = diagnosticoSelect.options[diagnosticoSelect.selectedIndex].text;
                
        if (selectedOptionText === 'Otro') {
            diagnosticoTextoInput.disabled = false;
            diagnosticoTextoInput.placeholder = 'Escribe el diagnóstico aquí...';
        } else {
            diagnosticoTextoInput.disabled = true;
            diagnosticoTextoInput.value = '';
            diagnosticoTextoInput.placeholder = '';
        }
    }

    toggleOtroDiagnostico();
    diagnosticoSelect.addEventListener('change', toggleOtroDiagnostico);
});

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