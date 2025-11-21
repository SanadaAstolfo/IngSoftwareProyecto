/**
 * Utilidades para formatear y validar RUT chileno
 * Formato: XX.XXX.XXX-X o X.XXX.XXX-X
 */

/**
 * Formatea un RUT agregando puntos y guión
 * @param {string} rut - RUT sin formato o parcialmente formateado
 * @returns {string} RUT formateado (ej: 12.345.678-9)
 */
function formatRut(rut) {
    // Eliminar todo excepto números y K/k
    let value = rut.replace(/[^0-9kK]/g, '');
    
    // Convertir k minúscula a mayúscula
    value = value.replace(/k/g, 'K');
    
    // Si está vacío, retornar vacío
    if (value.length === 0) return '';
    
    // Si tiene menos de 2 caracteres, no formatear
    if (value.length < 2) return value;
    
    // Separar dígito verificador (último carácter)
    let dv = value.slice(-1);
    let numero = value.slice(0, -1);
    
    // Formatear con puntos (de derecha a izquierda)
    let formatted = '';
    let count = 0;
    
    for (let i = numero.length - 1; i >= 0; i--) {
        if (count === 3) {
            formatted = '.' + formatted;
            count = 0;
        }
        formatted = numero[i] + formatted;
        count++;
    }
    
    // Agregar guión y dígito verificador
    return formatted + '-' + dv;
}

/**
 * Limpia el formato del RUT dejando solo números y K
 * @param {string} rut - RUT formateado
 * @returns {string} RUT sin formato (ej: 12345678-9)
 */
function cleanRut(rut) {
    return rut.replace(/\./g, '');
}

/**
 * Calcula el dígito verificador de un RUT
 * @param {string} rut - RUT sin dígito verificador
 * @returns {string} Dígito verificador (0-9 o K)
 */
function calculateDV(rut) {
    let suma = 0;
    let multiplo = 2;
    
    // Recorrer de derecha a izquierda
    for (let i = rut.length - 1; i >= 0; i--) {
        suma += parseInt(rut.charAt(i)) * multiplo;
        multiplo = multiplo < 7 ? multiplo + 1 : 2;
    }
    
    const dvEsperado = 11 - (suma % 11);
    
    if (dvEsperado === 11) return '0';
    if (dvEsperado === 10) return 'K';
    return dvEsperado.toString();
}

/**
 * Valida si un RUT es válido
 * @param {string} rut - RUT completo (con o sin formato)
 * @returns {boolean} true si el RUT es válido
 */
function validateRut(rut) {
    // Limpiar el RUT
    const cleanedRut = rut.replace(/[^0-9kK]/g, '');
    
    // Debe tener al menos 2 caracteres (número + DV)
    if (cleanedRut.length < 2) return false;
    
    // Separar número y DV
    const numero = cleanedRut.slice(0, -1);
    const dv = cleanedRut.slice(-1).toUpperCase();
    
    // Validar que el número sea válido
    if (!/^\d+$/.test(numero)) return false;
    
    // Calcular y comparar DV
    const dvCalculado = calculateDV(numero);
    
    return dv === dvCalculado;
}

/**
 * Aplica formato automático a un campo de input de RUT
 * @param {HTMLInputElement} input - Elemento input del RUT
 * @param {boolean} validateOnBlur - Si debe validar al perder el foco
 */
function applyRutFormat(input, validateOnBlur = false) {
    if (!input) return;
    
    // Evento para formatear mientras escribe
    input.addEventListener('input', function(e) {
        let cursorPosition = this.selectionStart;
        let oldLength = this.value.length;
        
        // Formatear el valor
        this.value = formatRut(this.value);
        
        // Ajustar posición del cursor
        let newLength = this.value.length;
        if (newLength > oldLength) {
            cursorPosition += (newLength - oldLength);
        }
        
        this.setSelectionRange(cursorPosition, cursorPosition);
    });
    
    // Evento para validar al perder el foco
    input.addEventListener('blur', function() {
        if (this.value) {
            this.value = formatRut(this.value);
            
            // Validar si está habilitado
            if (validateOnBlur) {
                const isValid = validateRut(this.value);
                
                if (isValid) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            }
        }
    });
}

/**
 * Inicializa el formateo automático para todos los campos de RUT en la página
 * Busca campos con: id que contenga 'rut', name que contenga 'rut', o data-format="rut"
 */
function initRutFormatting() {
    // Buscar todos los inputs que puedan ser RUT
    const rutInputs = document.querySelectorAll(
        'input[id*="rut" i], input[name*="rut" i], input[data-format="rut"]'
    );
    
    rutInputs.forEach(input => {
        // No aplicar a campos de tipo hidden o readonly
        if (input.type !== 'hidden' && !input.readOnly) {
            const shouldValidate = input.hasAttribute('data-validate-rut');
            applyRutFormat(input, shouldValidate);
        }
    });
}

/**
 * Limpia RUTs antes de enviar un formulario
 * Esto asegura que se envíen sin puntos para el backend
 */
function setupFormRutCleaning(form) {
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        const rutInputs = form.querySelectorAll(
            'input[id*="rut" i], input[name*="rut" i], input[data-format="rut"]'
        );
        
        rutInputs.forEach(input => {
            if (input.value && !input.hasAttribute('data-keep-format')) {
                input.value = cleanRut(input.value);
            }
        });
    });
}

// Auto-inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initRutFormatting);
} else {
    initRutFormatting();
}
