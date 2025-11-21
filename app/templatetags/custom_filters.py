from django import template

register = template.Library()

@register.filter
def format_rut(rut):
    """
    Formatea un RUT chileno con puntos y guión.
    Ejemplo: 12345678-9 -> 12.345.678-9
    """
    if not rut:
        return rut
    
    # Convertir a string y limpiar espacios
    rut = str(rut).strip()
    
    # Si ya tiene formato, retornarlo
    if '.' in rut:
        return rut
    
    # Separar número y dígito verificador
    if '-' in rut:
        numero, dv = rut.split('-')
    else:
        # Si no tiene guión, asumir que el último carácter es el DV
        numero = rut[:-1]
        dv = rut[-1]
    
    # Limpiar cualquier carácter no numérico del número
    numero = ''.join(filter(str.isdigit, numero))
    
    # Formatear con puntos
    numero_formateado = ""
    for i, digito in enumerate(reversed(numero)):
        if i > 0 and i % 3 == 0:
            numero_formateado = "." + numero_formateado
        numero_formateado = digito + numero_formateado
    
    return f"{numero_formateado}-{dv}"
