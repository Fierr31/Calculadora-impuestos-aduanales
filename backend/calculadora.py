import re

#preciounit = "12.3"
#cantidad = "550"
#pais = "cuba"
#flete = "5100"
#seguro = "1000"
#impuesto = "AMX (10%+0.36 Dls por Kg de azúcar)"

#entradas = [preciounit, cantidad, pais, flete, seguro, impuesto]

tratado = ["alemania", "austria", "australia", "belgica", "bolivia", "brunei", "canada", "chile", "colombia", "costa rica", "cuba", "dinamarca", "el salvador", "eslovaquia", "eslovenia", "españa", "estados unidos", "estonia", "finlandia", "francia", "grecia", "guatemala", "honduras", "hungria", "irlanda", "islandia", "israel", "italia", "japon", "letonia", "liechtenstein", "lituania", "luxemburgo", "malasia", "malta", "nicaragua", "noruega", "nueva zelanda", "paises bajos", "panama", "peru", "polonia", "portugal", "reino unido", "republica checa", "singapur", "suecia", "suiza", "uruguay", "vietnam"]

def basegravable(entradas):

    impuesto = entradas.impuesto

    if impuesto.strip().lower() == "prohibida":
        return {
            "status": "prohibido",
            "mensaje": "La mercancía está prohibida y no puede importarse."
        }
    try:
        porcentaje = float(impuesto)
        dls_kg = 0
    except ValueError:
        porcentaje_match = re.search(r'(\d+(?:\.\d+)?)%', impuesto)
        dls_kg_match = re.search(r'(\d+(?:\.\d+)?)\s*Dls', impuesto)

        porcentaje = float(porcentaje_match.group(1)) if porcentaje_match else 0
        dls_kg = float(dls_kg_match.group(1)) if dls_kg_match else 0

    va = (
        int(entradas.cantidad) * float(entradas.precio)
        + float(entradas.flete)
        + float(entradas.seguro)
    )

    if entradas.pais.lower() in tratado:
        dta = 425
    else:
        dta = (0.008 * va) / 100

    igi = ((porcentaje * va) / 100) + dls_kg * int(entradas.cantidad)
    base_grav = va + igi + dta

    return {
        "status": "ok",
        "valor_en_aduana": va,
        "igi": igi,
        "dta": dta,
        "base_gravable": base_grav,
        "porcentaje": porcentaje,
        "dls_per_cantidad": dls_kg
    }

#bg = basegravable(entradas)
#print(bg)