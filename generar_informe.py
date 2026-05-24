from pathlib import Path

from fpdf import FPDF
from owlready2 import *


# =============================================================================
# CONFIGURACIÓN
# =============================================================================

POBLADA_OWL    = Path("ontologia_poblada.rdf")
OUTPUT_PDF     = "Informe_Final_Riesgos_Multidominio.pdf"

ORDEN_TIPOS    = ["Activo", "Tarea", "Accion", "Efecto", "Condicion", "Linea Op.", "Objetivo"]

ACCIONES_MITIGACION = {
    "MUY BAJO": "Monitorizar",
    "BAJO":     "Respuesta local",
    "MEDIO":    "Aislar y contener",
    "ALTO":     "Despliegue de contingencia",
    "CRITICO":  "Escalada inmediata",
}


# =============================================================================
# CARGA DE LA ONTOLOGÍA
# =============================================================================

onto = get_ontology(str(POBLADA_OWL.resolve())).load()


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def construir_amenazas_por_activo():
    amenazas = {}
    for clase_inc in [onto.Ataque, onto.Sabotaje, onto.Fallo, onto.Interferencia]:
        for inc in clase_inc.instances():
            nombre_inc = inc.name.replace("INC_", "").replace("_", " ")
            for activo in inc.afectaA:
                amenazas.setdefault(activo.name, []).append(f"{nombre_inc} ({clase_inc.name})")
    return amenazas


def obtener_mision_padre(nodo_inicial):
    visitados = set()
    cola      = [nodo_inicial]
    while cola:
        nodo = cola.pop(0)
        if nodo in visitados:
            continue
        visitados.add(nodo)
        if isinstance(nodo, onto.Mision) or onto.Mision in getattr(nodo, "is_a", []):
            return nodo
        for prop in nodo.get_properties():
            if "contribuye" in prop.python_name.lower() or "escriticopara" in prop.python_name.lower():
                try:
                    for padre in prop[nodo]:
                        cola.append(padre)
                except Exception:
                    pass
    return None


def truncar(texto, n=30):
    return texto[:n] + ".." if len(texto) > n + 2 else texto


def obtener_score(nodo, attr, default):
    valores = getattr(nodo, attr, None)
    return valores[0] if valores else default


# =============================================================================
# FUNCIONES DE ESTILO PDF
# =============================================================================

def aplicar_color_texto(pdf_obj, nivel):
    n = nivel.upper()
    if n == "CRITICO":
        pdf_obj.set_text_color(220, 53, 69)
    elif n == "ALTO":
        pdf_obj.set_text_color(230, 115, 0)
    elif n == "MEDIO":
        pdf_obj.set_text_color(200, 150, 0)
    elif n == "BAJO":
        pdf_obj.set_text_color(40, 167, 69)
    elif n == "MUY BAJO":
        pdf_obj.set_text_color(21, 87, 36)
    else:
        pdf_obj.set_text_color(0, 0, 0)


def aplicar_color_fondo(pdf_obj, nivel):
    n = nivel.upper()
    if n == "CRITICO":
        pdf_obj.set_fill_color(220, 53, 69)
        pdf_obj.set_text_color(255, 255, 255)
    elif n == "ALTO":
        pdf_obj.set_fill_color(253, 126, 20)
        pdf_obj.set_text_color(255, 255, 255)
    elif n == "MEDIO":
        pdf_obj.set_fill_color(255, 193, 7)
        pdf_obj.set_text_color(0, 0, 0)
    elif n == "BAJO":
        pdf_obj.set_fill_color(40, 167, 69)
        pdf_obj.set_text_color(255, 255, 255)
    elif n == "MUY BAJO":
        pdf_obj.set_fill_color(21, 87, 36)
        pdf_obj.set_text_color(255, 255, 255)
    else:
        pdf_obj.set_fill_color(200, 200, 200)
        pdf_obj.set_text_color(0, 0, 0)


def cabecera_tabla(pdf_obj, cols):
    pdf_obj.set_fill_color(230, 230, 230)
    pdf_obj.set_text_color(0, 0, 0)
    pdf_obj.set_font("Arial", "B", 8)
    for ancho, texto in cols:
        pdf_obj.cell(w=ancho, h=10, txt=texto, border=1, ln=0, align="C", fill=True)
    pdf_obj.ln()


# =============================================================================
# EXTRACCIÓN DE DATOS
# =============================================================================

amenazas_por_activo = construir_amenazas_por_activo()

clases_red = {
    "Activo":     onto.Activo,
    "Tarea":      onto.Tarea,
    "Accion":     onto.Accion,
    "Efecto":     onto.Efecto,
    "Condicion":  onto.Condicion_Decisiva,
    "Linea Op.":  onto.Linea_Operacion,
    "Objetivo":   onto.Objetivo,
}


# =============================================================================
# GENERACIÓN DEL PDF
# =============================================================================

pdf     = FPDF()
misiones = list(onto.Mision.instances())

if not misiones:
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(w=0, h=10, txt="ERROR: No hay misiones en la ontología", border=0, ln=1, align="L")
    pdf.output(OUTPUT_PDF)
    exit()

for mision in misiones:
    pdf.add_page()

    #CABECERA 
    nombre_m = mision.name.replace("Mision_", "").replace("_", " ")
    pdf.set_fill_color(40, 40, 60)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(w=0, h=15, txt=f"  INFORME DE RIESGOS - MISION: {nombre_m}",
             border=0, ln=1, align="C", fill=True)
    pdf.ln(5)

    #1. EVALUACIÓN GLOBAL 
    ei_m = obtener_score(mision, "etiquetaInherente", "MUY BAJO")
    si_m = obtener_score(mision, "scoreInherente",    0.0)
    er_m = obtener_score(mision, "etiquetaResidual",  "MUY BAJO")
    sr_m = obtener_score(mision, "scoreResidual",     0.0)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(w=0, h=10, txt="1. EVALUACION GLOBAL DE LA MISION", border=0, ln=1, align="L")

    pdf.set_font("Arial", "B", 11)
    pdf.cell(w=70, h=10, txt="Riesgo Inherente:", border=0, ln=0, align="L")
    aplicar_color_fondo(pdf, ei_m)
    pdf.cell(w=45, h=10, txt=f"{ei_m} ({si_m:.2f})", border=1, ln=1, align="C", fill=True)

    pdf.set_text_color(0, 0, 0)
    pdf.cell(w=70, h=10, txt="Riesgo Residual:", border=0, ln=0, align="L")
    aplicar_color_fondo(pdf, er_m)
    pdf.cell(w=45, h=10, txt=f"{er_m} ({sr_m:.2f})", border=1, ln=1, align="C", fill=True)
    pdf.ln(10)

    #RECOPILACIÓN DE NODOS DE LA MISIÓN 
    nodos_mision         = []
    activos_con_amenazas = []

    for t_str, clase_obj in clases_red.items():
        for nodo in clase_obj.instances():
            if obtener_mision_padre(nodo) != mision:
                continue

            ei          = obtener_score(nodo, "etiquetaInherente", "MUY BAJO")
            si          = obtener_score(nodo, "scoreInherente",    0.0)
            er          = obtener_score(nodo, "etiquetaResidual",  "MUY BAJO")
            sr          = obtener_score(nodo, "scoreResidual",     0.0)
            nombre_limpio = nodo.name.split("_", 1)[-1].replace("_", " ")

            if t_str == "Activo":
                lista_amenazas = amenazas_por_activo.get(nodo.name, [])
                if lista_amenazas:
                    activos_con_amenazas.append({
                        "nombre":   nombre_limpio,
                        "amenazas": " + ".join(lista_amenazas),
                    })

            nodos_mision.append({
                "nombre": nombre_limpio,
                "tipo":   t_str,
                "ei":     ei,
                "si":     si,
                "er":     er,
                "sr":     sr,
                "mitig":  ACCIONES_MITIGACION.get(ei.upper(), "Monitorizar"),
            })

    nodos_mision.sort(key=lambda x: ORDEN_TIPOS.index(x["tipo"]))

    #2. NODOS DE ATENCIÓN PRIORITARIA 
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(w=0, h=10, txt="2. NODOS DE ATENCION PRIORITARIA", border=0, ln=1, align="L")

    cols_tabla = [(20, "Tipo"), (50, "Nombre"), (35, "Riesgo Inherente"),
                  (50, "Mitigacion"), (35, "Riesgo Residual")]
    cabecera_tabla(pdf, cols_tabla)

    criticos = [n for n in nodos_mision if n["ei"] in ["ALTO", "CRITICO"]]
    if not criticos:
        pdf.set_font("Arial", "", 8)
        pdf.cell(w=190, h=10, txt="No hay nodos en riesgo alto/critico en esta mision.",
                 border=1, ln=1, align="C")
    else:
        for n in criticos:
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", "", 8)
            pdf.cell(w=20, h=10, txt=n["tipo"],           border=1, ln=0, align="C")
            pdf.cell(w=50, h=10, txt=truncar(n["nombre"]), border=1, ln=0, align="C")

            pdf.set_font("Arial", "B", 8)
            aplicar_color_texto(pdf, n["ei"])
            pdf.cell(w=35, h=10, txt=f"{n['ei']} ({n['si']:.2f})", border=1, ln=0, align="C")

            pdf.set_text_color(80, 80, 80)
            pdf.set_font("Arial", "", 8)
            pdf.cell(w=50, h=10, txt=n["mitig"], border=1, ln=0, align="C")

            pdf.set_font("Arial", "B", 8)
            aplicar_color_texto(pdf, n["er"])
            pdf.cell(w=35, h=10, txt=f"{n['er']} ({n['sr']:.2f})", border=1, ln=1, align="C")

    pdf.ln(10)

    #3. AMENAZAS DETECTADAS EN ACTIVOS 
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(w=0, h=10, txt="3. AMENAZAS DETECTADAS EN ACTIVOS", border=0, ln=1, align="L")

    cabecera_tabla(pdf, [(60, "Activo Afectado"), (130, "Amenaza(s)")])

    if not activos_con_amenazas:
        pdf.set_font("Arial", "", 8)
        pdf.cell(w=190, h=10,
                 txt="No hay incidentes/amenazas registrados en activos de esta mision.",
                 border=1, ln=1, align="C")
    else:
        pdf.set_font("Arial", "", 8)
        for act in activos_con_amenazas:
            pdf.cell(w=60,  h=10, txt=truncar(act["nombre"],  35), border=1, ln=0, align="C")
            pdf.cell(w=130, h=10, txt=truncar(act["amenazas"], 85), border=1, ln=1, align="C")

    pdf.ln(10)

    #4. ESTADO GLOBAL DE LA RED
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(w=0, h=10, txt="4. ESTADO GLOBAL DE LA RED", border=0, ln=1, align="L")

    cabecera_tabla(pdf, cols_tabla)

    for n in nodos_mision:
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 8)
        pdf.cell(w=20, h=10, txt=n["tipo"],           border=1, ln=0, align="C")
        pdf.cell(w=50, h=10, txt=truncar(n["nombre"]), border=1, ln=0, align="C")

        pdf.set_font("Arial", "B", 8)
        aplicar_color_texto(pdf, n["ei"])
        pdf.cell(w=35, h=10, txt=f"{n['ei']} ({n['si']:.2f})", border=1, ln=0, align="C")

        pdf.set_text_color(80, 80, 80)
        pdf.set_font("Arial", "", 8)
        pdf.cell(w=50, h=10, txt=n["mitig"], border=1, ln=0, align="C")

        pdf.set_font("Arial", "B", 8)
        aplicar_color_texto(pdf, n["er"])
        pdf.cell(w=35, h=10, txt=f"{n['er']} ({n['sr']:.2f})", border=1, ln=1, align="C")


# =============================================================================
# GUARDADO DEL PDF
# =============================================================================

pdf.output(OUTPUT_PDF)
print(f"Archivo generado: {OUTPUT_PDF}")