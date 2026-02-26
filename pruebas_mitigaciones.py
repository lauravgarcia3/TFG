# ====================================================================
# LABORATORIO: LAS 3 OPCIONES GENERALIZADAS (PARA CUALQUIER NIVEL)
# ====================================================================

def normalizar(vector):
    max_val = max(vector.values())
    if max_val == 0: return vector
    return {k: v / max_val for k, v in vector.items()}

#  OPCIÓN 1 (Mezclar normalizado y sin normalizar)
def aplicar_mitigacion_mezcla(vector, factor, alpha=0.5):
    reducido = vector.copy()
    for k in reducido.keys():
        reducido[k] = reducido[k] * (1.0 - factor)
    
    reducido_norm = normalizar(reducido)
    
    nuevo = {}
    for k in vector.keys():
        nuevo[k] = (alpha * reducido[k]) + ((1.0 - alpha) * reducido_norm[k])
    return nuevo

#  OPCIÓN 2 EXPONENTE 
def aplicar_mitigacion_exponente(vector, factor):
    nuevo_sin_norm = vector.copy()
    exponente = 1.0 + factor 
    
    for k in vector.keys():
        nuevo_sin_norm[k] = vector[k] ** exponente 
        
    return nuevo_sin_norm, normalizar(nuevo_sin_norm)

# OPCIÓN 3 GENERALIZADA Desplazamiento hacia nieles inferiores
def aplicar_mitigacion_desplazamiento(vector, factor):
    nuevo = vector.copy()
    
    t_ma = vector["Muy Alta"] * factor
    nuevo["Muy Alta"] = max(0.0, nuevo["Muy Alta"] - t_ma)
    nuevo["Alta"] = min(1.0, nuevo["Alta"] + t_ma)
    
    t_a = vector["Alta"] * factor
    nuevo["Alta"] = max(0.0, nuevo["Alta"] - t_a)
    nuevo["Media"] = min(1.0, nuevo["Media"] + t_a)
    
    t_m = vector["Media"] * factor
    nuevo["Media"] = max(0.0, nuevo["Media"] - t_m)
    nuevo["Baja"] = min(1.0, nuevo["Baja"] + t_m)
    
    t_b = vector["Baja"] * factor
    nuevo["Baja"] = max(0.0, nuevo["Baja"] - t_b)
    nuevo["Muy Baja"] = min(1.0, nuevo["Muy Baja"] + t_b)
    
    t_mb = vector["Muy Baja"] * factor
    nuevo["Muy Baja"] = max(0.0, nuevo["Muy Baja"] - t_mb)
    
    return nuevo, normalizar(nuevo)




# ====================================================================
# EJECUCIÓN DEL TEST
# ====================================================================

if __name__ == "__main__":
    
    # CASO DE PRUEBA: Riesgo concentrado en MEDIO y BAJO
    vector_original = {"Muy Baja": 0.20, "Baja": 0.70, "Media": 1.00, "Alta": 0.00, "Muy Alta": 0.00}
    factor_mitigacion = 0.40  
    
    print(f"FACTOR DE MITIGACIÓN APLICADO: {factor_mitigacion*100}%\n")
    
    print("ESTADO INICIAL (Original)", vector_original)

    

    n = aplicar_mitigacion_mezcla(vector_original, factor_mitigacion)
    print("\nOPCIÓN 1: MEZCLA")
    print("RESULTADO", n)
 
    

    sin_n, con_n = aplicar_mitigacion_exponente(vector_original, factor_mitigacion)
    print("\nOPCIÓN 2: EXPONENTE")
    print("SIN normalizar", sin_n)
    print("CON normalización", con_n)
    

    sin_n, con_n = aplicar_mitigacion_desplazamiento(vector_original, factor_mitigacion)
    print("\nOPCIÓN 3: DESPLAZAMIENTO")
    print("SIN normalizar", sin_n)
    print("CON normalización", con_n)


    # CASO DE PRUEBA: Riesgo concentrado en Alto y Muy Alto
    vector_original = {"Muy Baja": 0.00, "Baja": 0.00, "Media": 0.30, "Alta": 1.00, "Muy Alta": 0.80}
    factor_mitigacion = 0.30  
    
    print(f"FACTOR DE MITIGACIÓN APLICADO: {factor_mitigacion*100}%\n")
    
    print("ESTADO INICIAL (Original)", vector_original)

    

    n = aplicar_mitigacion_mezcla(vector_original, factor_mitigacion)
    print("\nOPCIÓN 1: MEZCLA")
    print("RESULTADO", n)
 
    

    sin_n, con_n = aplicar_mitigacion_exponente(vector_original, factor_mitigacion)
    print("\nOPCIÓN 2: EXPONENTE")
    print("SIN normalizar", sin_n)
    print("CON normalización", con_n)
    

    sin_n, con_n = aplicar_mitigacion_desplazamiento(vector_original, factor_mitigacion)
    print("\nOPCIÓN 3: DESPLAZAMIENTO")
    print("SIN normalizar", sin_n)
    print("CON normalización", con_n)
    
    
 