#!/usr/bin/env python
"""
Script para compilar archivos .po a .mo sin necesidad de gettext
"""
import os
import struct

def compile_messages(locale_path):
    """Compila archivos .po a .mo"""
    for lang in ['en', 'es']:
        po_file = os.path.join(locale_path, lang, 'LC_MESSAGES', 'django.po')
        mo_file = os.path.join(locale_path, lang, 'LC_MESSAGES', 'django.mo')
        
        if os.path.exists(po_file):
            print(f"Compilando {po_file}...")
            compile_po_to_mo(po_file, mo_file)
        else:
            print(f"Archivo no encontrado: {po_file}")

def compile_po_to_mo(po_path, mo_path):
    """Compila un archivo .po a .mo"""
    import re
    
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraer pares msgid-msgstr
    pattern = r'^msgid\s+"(.+?)"\s*\nmsgstr\s+"(.+?)"'
    matches = re.findall(pattern, content, re.MULTILINE)
    
    translations = {}
    for msgid, msgstr in matches:
        if msgid:  # Ignorar header
            # Procesar escape sequences
            msgid = msgid.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
            msgstr = msgstr.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
            translations[msgid.encode('utf-8')] = msgstr.encode('utf-8')
    
    if not translations:
        # Crear archivo .mo vacío
        with open(mo_path, 'wb') as f:
            f.write(struct.pack('Iiiiiii', 0xde120495, 0, 0, 28, 28, 0, 0))
        print(f"  ✓ {mo_path} (vacío)")
        return
    
    # Construir el archivo .mo
    keys = sorted(translations.keys())
    offsets = []
    
    # Calcular offsets
    keyoffset = 7 * 4 + 16 * len(keys)
    valueoffset = keyoffset + sum(len(k) + 1 for k in keys)
    
    koffsets = []
    voffsets = []
    k = v = 0
    for key in keys:
        koffsets.append((len(key), keyoffset + k))
        k += len(key) + 1
        voffsets.append((len(translations[key]), valueoffset + v))
        v += len(translations[key]) + 1
    
    # Escribir archivo .mo
    with open(mo_path, 'wb') as f:
        # Header
        f.write(struct.pack('Iiiiiii', 0xde120495, 0, len(keys), 7*4, 7*4+len(keys)*8, 0, 0))
        
        # Key offsets
        for length, offset in koffsets:
            f.write(struct.pack('ii', length, offset))
        
        # Value offsets
        for length, offset in voffsets:
            f.write(struct.pack('ii', length, offset))
        
        # Keys
        for key in keys:
            f.write(key)
            f.write(b'\x00')
        
        # Values
        for key in keys:
            f.write(translations[key])
            f.write(b'\x00')
    
    print(f"  ✓ {mo_path} ({len(keys)} traducciones)")

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    locale_path = os.path.join(base_dir, 'locale')
    compile_messages(locale_path)
    print("Compilación completada.")
