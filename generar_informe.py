from owlready2 import *
from fpdf import FPDF
from pathlib import Path

# =============================================================================
# 1. CONFIGURACIÓN Y EXTRACCIÓN
# =============================================================================
POBLADA_OWL = Path("ontologia_poblada.rdf")
onto = get_ontology(str(POBLADA_OWL.resolve())).load()

ORDEN_TIPOS = ["Activo", "Tarea", "Accion", "Efecto", "Condicion", "Linea Op.", "Objetivo"]

ACCIONES_MITIGACION = {
    "MUY BAJO": "Monitorizar",
    "BAJO": "Respuesta local",
    "MEDIO": "Aislar y contener",
    "ALTO": "Despliegue de contingencia",
    "CRITICO": "Escalada inmediata"
}

amenazas_por_activo = {}
for clase_inc in [onto.Ataque, onto.Sabotaje, onto.Fallo, onto.Interferencia]:
    for inc in clase_inc.instances():
        nombre_incidente = inc.name.replace('INC_', '').replace('_', ' ')
        for activo_afectado in inc.afectaA:
            if activo_afectado.name not in amenazas_por_activo:
                amenazas_por_activo[activo_afectado.name] = []
            amenazas_por_activo[activo_afectado.name].append(f"{nombre_incidente} ({clase_inc.name})")

def obtener_mision_padre(nodo_inicial):
    visitados = set()
    cola = [nodo_inicial]
    while cola:
        nodo = cola.pop(0)
        if nodo in visitados: continue
        visitados.add(nodo)
        if isinstance(nodo, onto.Mision) or onto.Mision in getattr(nodo, 'is_a', []):
            return nodo
        for prop in nodo.get_properties():
            if "contribuye" in prop.python_name.lower() or "escriticopara" in prop.python_name.lower():
                try:
                    for padre in prop[nodo]: cola.append(padre)
                except: pass
    return None

# =============================================================================
# FUNCIONES DE ESTILO
# =============================================================================
def aplicar_color_texto(pdf_obj, nivel):
    n = nivel.upper()
    if n == "CRITICO":    pdf_obj.set_text_color(220, 53, 69)  
    elif n == "ALTO":     pdf_obj.set_text_color(230, 115, 0)  
    elif n == "MEDIO":    pdf_obj.set_text_color(200, 150, 0)  
    elif n == "BAJO":     pdf_obj.set_text_color(40, 167, 69)  
    elif n == "MUY BAJO": pdf_obj.set_text_color(21, 87, 36)   
    else:                 pdf_obj.set_text_color(0, 0, 0)

def aplicar_color_fondo(pdf_obj, nivel):
    n = nivel.upper()
    if n == "CRITICO":    pdf_obj.set_fill_color(220, 53, 69); pdf_obj.set_text_color(255, 255, 255)
    elif n == "ALTO":     pdf_obj.set_fill_color(253, 126, 20); pdf_obj.set_text_color(255, 255, 255)
    elif n == "MEDIO":    pdf_obj.set_fill_color(255, 193, 7);  pdf_obj.set_text_color(0, 0, 0)
    elif n == "BAJO":     pdf_obj.set_fill_color(40, 167, 69);  pdf_obj.set_text_color(255, 255, 255)
    elif n == "MUY BAJO": pdf_obj.set_fill_color(21, 87, 36);   pdf_obj.set_text_color(255, 255, 255)
    else:                 pdf_obj.set_fill_color(200, 200, 200); pdf_obj.set_text_color(0, 0, 0)

# =============================================================================
# GENERACIÓN DEL PDF
# =============================================================================
pdf = FPDF()

misiones = list(onto.Mision.instances())
if not misiones:
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(w=0, h=10, txt="ERROR: No hay misiones en la ontología", border=0, ln=1, align='L')
    pdf.output("Informe_Final_Riesgos_Multidominio.pdf")
    exit()

for mision in misiones:
    pdf.add_page()
    
    # --- CABECERA ---
    pdf.set_fill_color(40, 40, 60)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 16)
    nombre_m = mision.name.replace("Mision_", "").replace("_", " ")
    pdf.cell(w=0, h=15, txt=f"  INFORME DE RIESGOS - MISION: {nombre_m}", border=0, ln=1, align='C', fill=True)
    pdf.ln(5)

    # --- 1. RESUMEN GLOBAL ---
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(w=0, h=10, txt="1. EVALUACION GLOBAL DE LA MISION", border=0, ln=1, align='L')
    
    ei_m = mision.etiquetaInherente[0] if hasattr(mision, "etiquetaInherente") and mision.etiquetaInherente else "MUY BAJO"
    si_m = mision.scoreInherente[0] if hasattr(mision, "scoreInherente") and mision.scoreInherente else 0.0
    er_m = mision.etiquetaResidual[0] if hasattr(mision, "etiquetaResidual") and mision.etiquetaResidual else "MUY BAJO"
    sr_m = mision.scoreResidual[0] if hasattr(mision, "scoreResidual") and mision.scoreResidual else 0.0

    pdf.set_font("Arial", 'B', 11)
    pdf.cell(w=70, h=10, txt="Riesgo Inherente:", border=0, ln=0, align='L')
    aplicar_color_fondo(pdf, ei_m)
    pdf.cell(w=45, h=10, txt=f"{ei_m} ({si_m:.2f})", border=1, ln=1, align='C', fill=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.cell(w=70, h=10, txt="Riesgo Residual:", border=0, ln=0, align='L')
    aplicar_color_fondo(pdf, er_m)
    pdf.cell(w=45, h=10, txt=f"{er_m} ({sr_m:.2f})", border=1, ln=1, align='C', fill=True)
    pdf.ln(10)

    # --- RECOPILAR NODOS ---
    nodos_mision = []
    activos_con_amenazas = []
    clases_red = {
        "Activo": onto.Activo, "Tarea": onto.Tarea, "Accion": onto.Accion, 
        "Efecto": onto.Efecto, "Condicion": onto.Condicion_Decisiva, 
        "Linea Op.": onto.Linea_Operacion, "Objetivo": onto.Objetivo
    }

    for t_str, clase_obj in clases_red.items():
        for nodo in clase_obj.instances():
            if obtener_mision_padre(nodo) == mision:
                ei = nodo.etiquetaInherente[0] if hasattr(nodo, "etiquetaInherente") and nodo.etiquetaInherente else "MUY BAJO"
                si = nodo.scoreInherente[0] if hasattr(nodo, "scoreInherente") and nodo.scoreInherente else 0.0
                er = nodo.etiquetaResidual[0] if hasattr(nodo, "etiquetaResidual") and nodo.etiquetaResidual else "MUY BAJO"
                sr = nodo.scoreResidual[0] if hasattr(nodo, "scoreResidual") and nodo.scoreResidual else 0.0
                
                nombre_limpio = nodo.name.split("_", 1)[-1].replace("_", " ")
                
                # Guardamos los activos que sufren ataques para la nueva tabla
                if t_str == "Activo":
                    lista_amenazas = amenazas_por_activo.get(nodo.name, [])
                    if lista_amenazas:
                        amnz_str = " + ".join(lista_amenazas)
                        activos_con_amenazas.append({
                            "nombre": nombre_limpio,
                            "amenazas": amnz_str
                        })

                nodos_mision.append({
                    "nombre": nombre_limpio,
                    "tipo": t_str, "ei": ei, "si": si, "er": er, "sr": sr,
                    "mitig": ACCIONES_MITIGACION.get(ei.upper(), "Monitorizar")
                })

    nodos_mision.sort(key=lambda x: ORDEN_TIPOS.index(x["tipo"]))

    # --- 2. TABLA NODOS CRÍTICOS ---
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(w=0, h=10, txt="2. NODOS DE ATENCION PRIORITARIA", border=0, ln=1, align='L')

    pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", 'B', 8)
    pdf.cell(w=20, h=10, txt="Tipo", border=1, ln=0, align='C', fill=True)
    pdf.cell(w=50, h=10, txt="Nombre", border=1, ln=0, align='C', fill=True)
    pdf.cell(w=35, h=10, txt="Riesgo Inherente", border=1, ln=0, align='C', fill=True)
    pdf.cell(w=50, h=10, txt="Mitigacion", border=1, ln=0, align='C', fill=True)
    pdf.cell(w=35, h=10, txt="Riesgo Residual", border=1, ln=1, align='C', fill=True)

    criticos = [n for n in nodos_mision if n["ei"] in ["ALTO", "CRITICO"]]
    if not criticos:
        pdf.set_font("Arial", '', 8)
        pdf.cell(w=190, h=10, txt="No hay nodos en riesgo alto/critico en esta mision.", border=1, ln=1, align='C')
    else:
        for n in criticos:
            pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", '', 8)
            
            nom_txt = n["nombre"][:30] + ".." if len(n["nombre"]) > 32 else n["nombre"]
            
            pdf.cell(w=20, h=10, txt=n["tipo"], border=1, ln=0, align='C')
            pdf.cell(w=50, h=10, txt=nom_txt, border=1, ln=0, align='C')
            
            pdf.set_font("Arial", 'B', 8); aplicar_color_texto(pdf, n["ei"])
            pdf.cell(w=35, h=10, txt=f"{n['ei']} ({n['si']:.2f})", border=1, ln=0, align='C')
            
            pdf.set_text_color(80, 80, 80); pdf.set_font("Arial", '', 8)
            pdf.cell(w=50, h=10, txt=n["mitig"], border=1, ln=0, align='C')
            
            pdf.set_font("Arial", 'B', 8); aplicar_color_texto(pdf, n["er"])
            pdf.cell(w=35, h=10, txt=f"{n['er']} ({n['sr']:.2f})", border=1, ln=1, align='C')
    pdf.ln(10)

    # --- 3. TABLA DE AMENAZAS EN ACTIVOS ---
    pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 12)
    pdf.cell(w=0, h=10, txt="3. AMENAZAS DETECTADAS EN ACTIVOS", border=0, ln=1, align='L')
    
    pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", 'B', 8)
    pdf.cell(w=60, h=10, txt="Activo Afectado", border=1, ln=0, align='C', fill=True)
    pdf.cell(w=130, h=10, txt="Amenaza(s)", border=1, ln=1, align='C', fill=True)

    if not activos_con_amenazas:
        pdf.set_font("Arial", '', 8)
        pdf.cell(w=190, h=10, txt="No hay incidentes/amenazas registrados en activos de esta mision.", border=1, ln=1, align='C')
    else:
        pdf.set_font("Arial", '', 8)
        for act in activos_con_amenazas:
            nom_act = act["nombre"][:35] + ".." if len(act["nombre"]) > 37 else act["nombre"]
            amnz_txt = act["amenazas"][:85] + ".." if len(act["amenazas"]) > 87 else act["amenazas"]
            
            pdf.cell(w=60, h=10, txt=nom_act, border=1, ln=0, align='C')
            pdf.cell(w=130, h=10, txt=amnz_txt, border=1, ln=1, align='C')

    pdf.ln(10)

    # --- 4. ESTADO GLOBAL ---
    pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 12)
    pdf.cell(w=0, h=10, txt="4. ESTADO GLOBAL DE LA RED", border=0, ln=1, align='L')
    
    pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", 'B', 8)
    pdf.cell(w=20, h=10, txt="Tipo", border=1, ln=0, align='C', fill=True)
    pdf.cell(w=50, h=10, txt="Nombre", border=1, ln=0, align='C', fill=True)
    pdf.cell(w=35, h=10, txt="Riesgo Inherente", border=1, ln=0, align='C', fill=True)
    pdf.cell(w=50, h=10, txt="Mitigacion", border=1, ln=0, align='C', fill=True)
    pdf.cell(w=35, h=10, txt="Riesgo Residual", border=1, ln=1, align='C', fill=True)

    for n in nodos_mision:
        pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", '', 8)
        
        nom_txt2 = n["nombre"][:30] + ".." if len(n["nombre"]) > 32 else n["nombre"]
        
        pdf.cell(w=20, h=10, txt=n["tipo"], border=1, ln=0, align='C')
        pdf.cell(w=50, h=10, txt=nom_txt2, border=1, ln=0, align='C')
        
        pdf.set_font("Arial", 'B', 8); aplicar_color_texto(pdf, n["ei"])
        pdf.cell(w=35, h=10, txt=f"{n['ei']} ({n['si']:.2f})", border=1, ln=0, align='C')
        
        pdf.set_text_color(80, 80, 80); pdf.set_font("Arial", '', 8)
        pdf.cell(w=50, h=10, txt=n["mitig"], border=1, ln=0, align='C')
        
        pdf.set_font("Arial", 'B', 8); aplicar_color_texto(pdf, n["er"])
        pdf.cell(w=35, h=10, txt=f"{n['er']} ({n['sr']:.2f})", border=1, ln=1, align='C')


pdf.output("Informe_Final_Riesgos_Multidominio.pdf")
print("¡Archivo generado: Informe_Final_Riesgos_Multidominio.pdf!")