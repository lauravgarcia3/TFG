from owlready2 import *
from pathlib import Path
import json

# CONFIGURACIÓN

BASE_OWL = Path("ontologia_base.rdf")
OUTPUT_OWL = Path("ontologia_poblada.rdf")
JSON_FILE = Path("escenario.json")

# CARGA

onto = get_ontology(str(BASE_OWL.resolve())).load()

with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

Activo = onto.Activo
Interferencia = onto.Interferencia 
Mision = onto.Mision
Riesgo = onto.Riesgo
Dominio = onto.Dominio  
Fase = onto.Fase        

# Instanciamos las nuevas clases del árbol
Objetivo = onto.Objetivo
Linea_Operacion = onto.Linea_Operacion
Condicion_Decisiva = onto.Condicion_Decisiva
Efecto = onto.Efecto
Actividad = onto.Actividad
Tarea = onto.Tarea

prop_activo_dominio = onto.search_one(iri="*activoRelacionadoConDominio")

def obtener_individuo(clase_padre, nombre_individuo):
    iri_busqueda = f"*{nombre_individuo}"
    instancia = onto.search_one(iri=iri_busqueda)
    
    if not instancia:
        instancia = clase_padre(nombre_individuo)
    
    return instancia

# 1. MISIONES
for m_data in data.get("misiones", []):
    mision = Mision(m_data["id"])
    
    fase_ind = obtener_individuo(Fase, m_data.get('fase', 'Planeamiento'))
    if fase_ind: mision.estaEnFase = [fase_ind]
    
    for dom_name in m_data.get("dominios", []):
        dom_ind = obtener_individuo(Dominio, dom_name)
        if dom_ind: mision.misionOperaEnDominio.append(dom_ind)

# 2. OBJETIVOS
for o_data in data.get("objetivos", []):
    obj = Objetivo(o_data["id"])
    padre = onto.search_one(iri=f"*{o_data['contribuyeA']}")
    if padre: obj.contribuyeAMision.append(padre)
    if "peso" in o_data: obj.pesoJerarquico = [float(o_data["peso"])]

# 3. LÍNEAS DE OPERACIÓN
for lo_data in data.get("lineas_operacion", []):
    lo = Linea_Operacion(lo_data["id"])
    padre = onto.search_one(iri=f"*{lo_data['contribuyeA']}")
    if padre: lo.contribuyeAObjetivo.append(padre)
    if "peso" in lo_data: lo.pesoJerarquico = [float(lo_data["peso"])]

# 4. CONDICIONES DECISIVAS
for cd_data in data.get("condiciones_decisivas", []):
    cd = Condicion_Decisiva(cd_data["id"])
    padre = onto.search_one(iri=f"*{cd_data['contribuyeA']}")
    if padre: cd.contribuyeALinea.append(padre)
    if "peso" in cd_data: cd.pesoJerarquico = [float(cd_data["peso"])]
    if "umbral" in cd_data: cd.umbralDecision = [float(cd_data["umbral"])]

# 5. EFECTOS
for ef_data in data.get("efectos", []):
    ef = Efecto(ef_data["id"])
    padre = onto.search_one(iri=f"*{ef_data['contribuyeA']}")
    if padre: ef.contribuyeACondicion.append(padre)
    if "peso" in ef_data: ef.pesoJerarquico = [float(ef_data["peso"])]

# 6. ACTIVIDADES
for act_data in data.get("actividades", []):
    act = Actividad(act_data["id"])
    padre = onto.search_one(iri=f"*{act_data['contribuyeA']}")
    if padre: act.contribuyeAEfecto.append(padre)
    if "peso" in act_data: act.pesoJerarquico = [float(act_data["peso"])]

# 7. TAREAS
for t_data in data.get("tareas", []):
    tarea = Tarea(t_data["id"])
    padre = onto.search_one(iri=f"*{t_data['contribuyeA']}")
    if padre: tarea.contribuyeAActividad.append(padre)
    if "peso" in t_data: tarea.pesoJerarquico = [float(t_data["peso"])]

# 8. ACTIVOS (Aquí se corrige el error del KeyError)
for a_data in data.get("activos", []):
    activo = Activo(a_data["id"])
    activo.criticidad = [float(a_data["criticidad"])]
    if "peso" in a_data: activo.pesoJerarquico = [float(a_data["peso"])]
    
    padre = onto.search_one(iri=f"*{a_data['contribuyeA']}")
    if padre: activo.contribuyeATarea.append(padre)

    if "dominios" in a_data:
        for dom_name in a_data["dominios"]:
            dom_ind = obtener_individuo(Dominio, dom_name)
            if dom_ind and prop_activo_dominio:
                prop_activo_dominio[activo].append(dom_ind)

# 9. INCIDENTES
for i_data in data.get("incidentes", []):
    incidente = Interferencia(i_data["id"])
    for act_id in i_data.get("afectaA", []):
        act_rel = onto.search_one(iri=f"*{act_id}")
        if act_rel: incidente.afectaA.append(act_rel)
    for dom_name in i_data.get("dominios", []):
        dom_ind = obtener_individuo(Dominio, dom_name)
        if dom_ind: incidente.incidenteAfectaADominio.append(dom_ind)

# 10. RIESGOS
for r_data in data.get("riesgos", []):
    riesgo = Riesgo(r_data["id"])

try:
    if OUTPUT_OWL.exists(): OUTPUT_OWL.unlink()
    onto.save(file=str(OUTPUT_OWL.resolve()))
except Exception as e:
    print("ERROR al guardar la ontologia")