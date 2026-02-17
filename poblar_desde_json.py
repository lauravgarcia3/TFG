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


prop_activo_dominio = onto.search_one(iri="*activoRelacionadoConDominio")




def obtener_individuo(clase_padre, nombre_individuo):
    iri_busqueda = f"*{nombre_individuo}"
    instancia = onto.search_one(iri=iri_busqueda)
    
    if not instancia:
        instancia = clase_padre(nombre_individuo)
    
    return instancia


for m_data in data["misiones"]:
    mision = Mision(m_data["id"])
    
    # Fase
    fase_ind = obtener_individuo(Fase, m_data['fase'])
    if fase_ind: mision.estaEnFase = [fase_ind]
    
    # Dominios Misión
    for dom_name in m_data["dominios"]:
        dom_ind = obtener_individuo(Dominio, dom_name)
        if dom_ind: mision.misionOperaEnDominio.append(dom_ind)

# 2. ACTIVOS

for a_data in data["activos"]:
    activo = Activo(a_data["id"])
    activo.criticidad = [float(a_data["criticidad"])]
    
    m_rel = onto.search_one(iri=f"*{a_data['perteneceAMision']}")
    if m_rel: activo.esCriticoPara.append(m_rel)

    # DOMINIOS DEL ACTIVO
    if "dominios" in a_data:
        for dom_name in a_data["dominios"]:
            dom_ind = obtener_individuo(Dominio, dom_name)
            if dom_ind and prop_activo_dominio:
                prop_activo_dominio[activo].append(dom_ind)
            else:
                print(f"     [ERROR] No se pudo relacionar con {dom_name}")

# 3. INCIDENTES
for i_data in data["incidentes"]:
    incidente = Interferencia(i_data["id"])
    for act_id in i_data["afectaA"]:
        act_rel = onto.search_one(iri=f"*{act_id}")
        if act_rel: incidente.afectaA.append(act_rel)
    for dom_name in i_data["dominios"]:
        dom_ind = obtener_individuo(Dominio, dom_name)
        if dom_ind: incidente.incidenteAfectaADominio.append(dom_ind)

for r_data in data["riesgos"]:
    riesgo = Riesgo(r_data["id"])

try:
    if OUTPUT_OWL.exists(): OUTPUT_OWL.unlink()
    onto.save(file=str(OUTPUT_OWL.resolve()))
except Exception as e:
    print("ERROR al guardar la ontologia")