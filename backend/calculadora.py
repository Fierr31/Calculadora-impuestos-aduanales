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
    
    if len(entradas[5]) > 3:
        porcentaje = re.search(r'(\d+(?:\.\d+)?)%', entradas[5])
        dls_kg = re.search(r'(\d+(?:\.\d+)?)\s*Dls', entradas[5])

        if porcentaje:
            porcentaje = float(porcentaje.group(1))

        if dls_kg:
            dls_kg = float(dls_kg.group(1))
    else:
        porcentaje = float(entradas[5])
        dls_kg = 0

    va = ((int(entradas[1]))*(float(entradas[0])))+float(entradas[3])+float(entradas[4])

    for i in tratado:
        if entradas[2] == i:
            dta = 425
            break
        else:
            dta = (0.008*va)/100

    igi = (porcentaje*va)/100 + va

    base_grav = va + igi + dta

    return {
        "valor_en_aduana":va, 
        "igi": igi,
        "dta": dta,
        "base_gravable": base_grav,
        "porcentaje": porcentaje,
        "dls_per_cantidad": dls_kg
        }

#bg = basegravable(entradas)
#print(bg)