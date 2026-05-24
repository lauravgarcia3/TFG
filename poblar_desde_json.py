import json
from pathlib import Path

from owlready2 import *


# CONFIGURACIÓN
BASE_OWL = Path("ontologia_base.rdf")
OUTPUT_OWL = Path("ontologia_poblada.rdf")
JSON_FILE = Path("caso_uso.json")

# CARGA DE LA ONTOLOGÍA BASE Y DEL FICHERO DE ENTRADA
onto = get_ontology(str(BASE_OWL.resolve())).load()

with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)


# CLASES DE LA ONTOLOGÍA
Activo = onto.Activo
Interferencia = onto.Interferencia 
Ataque = onto.Ataque
Sabotaje = onto.Sabotaje
Fallo = onto.Fallo
Mision = onto.Mision
Dominio = onto.Dominio  
Fase = onto.Fase        
Objetivo = onto.Objetivo
Linea_Operacion = onto.Linea_Operacion
Condicion_Decisiva = onto.Condicion_Decisiva
Efecto = onto.Efecto
Accion = onto.Accion  
Tarea = onto.Tarea


# FUNCION PARA OBTENER O CREAR INSTANCIAS 
def obtener_individuo(clase_padre, nombre_individuo):
    nombre_limpio = nombre_individuo.strip()
    
    iri_exacto = f"{onto.base_iri}{nombre_limpio}"
    instancia = onto.search_one(iri=iri_exacto)
    
    if not instancia:
        with onto:
            instancia = clase_padre(nombre_limpio)
            
    return instancia


# POBLADO DE LA ONTOLOGÍA

# 1. MISIONES
with onto:
    for m_data in data.get("misiones", []):
        mision = obtener_individuo(Mision, m_data["id"])
        
        fase_ind = obtener_individuo(Fase, m_data.get('fase', 'Planeamiento'))
        if fase_ind: mision.estaEnFase = [fase_ind]
        
        if "total_nodos_red" in m_data:
            mision.total_nodos_red = [int(m_data["total_nodos_red"])]
        
        for dom_name in m_data.get("dominios", []):
            dom_ind = obtener_individuo(Dominio, dom_name)
            if dom_ind and dom_ind not in mision.misionOperaEnDominio:
                mision.misionOperaEnDominio.append(dom_ind)

# 2. OBJETIVOS
with onto:
    for o_data in data.get("objetivos", []):
        obj = obtener_individuo(Objetivo, o_data["id"])
        padre = onto.search_one(iri=f"{onto.base_iri}{o_data['contribuyeA']}")
        if padre and padre not in obj.contribuyeAMision: 
            obj.contribuyeAMision.append(padre)
        if "peso" in o_data: obj.pesoJerarquico = [float(o_data["peso"])]

# 3. LÍNEAS DE OPERACIÓN
with onto:
    for lo_data in data.get("lineas_operacion", []):
        lo = obtener_individuo(Linea_Operacion, lo_data["id"])
        padre = onto.search_one(iri=f"{onto.base_iri}{lo_data['contribuyeA']}")
        if padre and padre not in lo.contribuyeAObjetivo: 
            lo.contribuyeAObjetivo.append(padre)
        if "peso" in lo_data: lo.pesoJerarquico = [float(lo_data["peso"])]

# 4. CONDICIONES DECISIVAS
with onto:
    for cd_data in data.get("condiciones_decisivas", []):
        cd = obtener_individuo(Condicion_Decisiva, cd_data["id"])
        padre = onto.search_one(iri=f"{onto.base_iri}{cd_data['contribuyeA']}")
        if padre and padre not in cd.contribuyeALinea: 
            cd.contribuyeALinea.append(padre)
        if "peso" in cd_data: cd.pesoJerarquico = [float(cd_data["peso"])]
        if "umbral" in cd_data: cd.umbralDecision = [float(cd_data["umbral"])]

# 5. EFECTOS
with onto:
    for ef_data in data.get("efectos", []):
        ef = obtener_individuo(Efecto, ef_data["id"])
        padre = onto.search_one(iri=f"{onto.base_iri}{ef_data['contribuyeA']}")
        if padre and padre not in ef.contribuyeACondicion: 
            ef.contribuyeACondicion.append(padre)
        if "peso" in ef_data: ef.pesoJerarquico = [float(ef_data["peso"])]

# 6. ACCIONES 
with onto:
    for act_data in data.get("acciones", []):
        acc = obtener_individuo(Accion, act_data["id"])
        padre = onto.search_one(iri=f"{onto.base_iri}{act_data['contribuyeA']}")
        if padre and padre not in acc.contribuyeAEfecto: 
            acc.contribuyeAEfecto.append(padre)
        if "peso" in act_data: acc.pesoJerarquico = [float(act_data["peso"])]

# 7. TAREAS
with onto:
    for t_data in data.get("tareas", []):
        tarea = obtener_individuo(Tarea, t_data["id"])
        padre = onto.search_one(iri=f"{onto.base_iri}{t_data['contribuyeA']}")
        if padre and padre not in tarea.contribuyeAAccion: 
            tarea.contribuyeAAccion.append(padre)  
        if "peso" in t_data: tarea.pesoJerarquico = [float(t_data["peso"])]

# 8. ACTIVOS 
with onto:
    for a_data in data.get("activos", []):
        activo = obtener_individuo(Activo, a_data["id"])
        
        criticidad_val = float(a_data["criticidad"])
        activo.criticidad = [criticidad_val]
        
        if "peso" in a_data: 
            activo.pesoJerarquico = [float(a_data["peso"])]
        
        if "conexiones_externas" in a_data:
            activo.numConexiones = [int(a_data["conexiones_externas"])]
        elif "numConexiones" in a_data:
            activo.numConexiones = [int(a_data["numConexiones"])]
            
        if "numDependencias" in a_data:
            activo.numDependencias = [int(a_data["numDependencias"])]
        if "tiene_redundancia" in a_data:
            activo.tieneRedundancia = [bool(a_data["tiene_redundancia"])]
        
        # Relacion con la tarea a la que contribuye
        padre = onto.search_one(iri=f"{onto.base_iri}{a_data['contribuyeA']}")
        if padre and padre not in activo.contribuyeATarea: 
            activo.contribuyeATarea.append(padre)

        # Dominios relacionados
        if "dominios" in a_data:
            for dom_name in a_data["dominios"]:
                dom_ind = obtener_individuo(Dominio, dom_name)
                if dom_ind and dom_ind not in activo.activoRelacionadoConDominio:
                    activo.activoRelacionadoConDominio.append(dom_ind)

        # Relación de criticidad con la misión
        if criticidad_val > 0.6:
            mision_id = a_data.get("perteneceAMision")
            if mision_id:
                padre_mision = onto.search_one(iri=f"{onto.base_iri}{mision_id}")
                if padre_mision and padre_mision not in activo.esCriticoPara:
                    activo.esCriticoPara.append(padre_mision)

# 9. INCIDENTES 
with onto:
    TIPO_A_CLASE = {
        "Ataque":       Ataque,
        "Sabotaje":     Sabotaje,
        "Fallo":        Fallo,
        "Interferencia": Interferencia,
    }

    for i_data in data.get("incidentes", []):
        clase_inc = TIPO_A_CLASE.get(i_data.get("tipo_incidente", "Fallo"), Fallo)
        incidente = obtener_individuo(clase_inc, i_data["id"])

        if "prob" in i_data:
            incidente.probabilidadIncidente = [float(i_data["prob"])]
        if "imp" in i_data:
            incidente.impactoIncidente = [float(i_data["imp"])]

        for act_id in i_data.get("afectaA", []):
            act_rel = onto.search_one(iri=f"{onto.base_iri}{act_id}")
            if act_rel and act_rel not in incidente.afectaA:
                incidente.afectaA.append(act_rel)

        for dom_name in i_data.get("dominios", []):
            dom_ind = obtener_individuo(Dominio, dom_name)
            if dom_ind and dom_ind not in incidente.incidenteAfectaADominio:
                incidente.incidenteAfectaADominio.append(dom_ind)


# GUARDADO DE LA ONTOLOGÍA POBLADA
try:
    if OUTPUT_OWL.exists(): OUTPUT_OWL.unlink()
    onto.save(file=str(OUTPUT_OWL.resolve()))
    print(f"\n[ÉXITO] Ontología poblada correctamente en: {OUTPUT_OWL.name}")
except Exception as e:
    print(f"\n[ERROR] Al guardar la ontologia: {e}")