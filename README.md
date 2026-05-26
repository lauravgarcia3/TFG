# Evaluación de riesgo de ciberseguridad en operaciones multidominio

Este repositorio contiene una prueba de concepto desarrollada en Python para evaluar el riesgo de ciberseguridad en operaciones multidominio. El sistema combina una representación semántica mediante ontología OWL con un motor de inferencia difusa, permitiendo calcular el riesgo inherente y residual de los elementos de una misión y propagar dichos valores a través de una estructura jerárquica.

El caso de uso incluido está formado por dos misiones: **Operación Costa** y **Convoy Tierra**.

## Contenido del repositorio

El repositorio contiene los siguientes ficheros principales:

- `motor_difuso.py` — módulo principal que implementa la lógica de evaluación de riesgo. Incluye el ajuste contextual de probabilidad e impacto, el motor de inferencia difusa, el cálculo del riesgo inherente y residual, y la propagación jerárquica a través de la estructura de la misión.

- `poblar_desde_json.py` — script que lee el fichero de entrada en formato JSON y genera la ontología poblada con los individuos, propiedades y relaciones del escenario.

- `generar_informe.py` — script que lee la ontología evaluada y genera el informe final en formato PDF con el resumen global de riesgos, los nodos de atención prioritaria y el estado completo de la red.

- `caso_uso.json` — fichero de entrada con la definición del escenario de validación. Contiene las dos misiones del caso de uso, Operación Costa y Convoy Tierra, junto con todos los elementos jerárquicos, activos, incidentes y parámetros de configuración.

- `ontologia_base.rdf` — ontología OWL con la estructura general del modelo: clases, propiedades y relaciones que definen el esquema de representación semántica de una operación multidominio.

- `ontologia_poblada.rdf` — ontología generada inicialmente tras ejecutar `poblar_desde_json.py` sobre el caso de uso incluido. Contiene los individuos del escenario y, tras la ejecución de `motor_difuso.py`, incorpora los valores de riesgo calculados y almacenados como propiedades de datos.

- `Informe_Final_Riesgos_Multidominio.pdf` — informe PDF generado por el sistema para el caso de uso de validación.

## Requisitos

Para ejecutar el sistema en local es necesario tener instalado **Python 3.9 o superior**.

En Windows, durante la instalación de Python, es recomendable marcar la opción:

`Add Python to PATH`

Para comprobar que Python está correctamente instalado, puede ejecutarse:

`python --version`

## Instalación de dependencias

Las dependencias necesarias son:

- `owlready2` — carga, manipulación y guardado de ontologías OWL.
- `scikit-fuzzy` — definición de funciones de pertenencia, inferencia difusa y defuzzificación.
- `scipy` — dependencia utilizada por `scikit-fuzzy` para operaciones matemáticas.
- `packaging` — dependencia utilizada por `scikit-fuzzy` para la gestión de versiones.
- `fpdf2` — generación del informe en formato PDF.
- `numpy` — operaciones numéricas utilizadas por el motor difuso.

Pueden instalarse todas con el siguiente comando:

`python -m pip install owlready2 scikit-fuzzy scipy packaging fpdf2 numpy`

## Ejecución

Para que la ejecución funcione correctamente, los siguientes ficheros deben encontrarse en el mismo directorio:

- `caso_uso.json`
- `ontologia_base.rdf`
- `poblar_desde_json.py`
- `motor_difuso.py`
- `generar_informe.py`

La ejecución debe realizarse desde una terminal situada en el directorio del proyecto.

Primero, se genera la ontología poblada a partir del fichero JSON:

`python .\poblar_desde_json.py`

Después, se ejecuta el motor difuso:

`python .\motor_difuso.py`

Este segundo script calcula los riesgos inherentes y residuales, actualiza la ontología poblada y lanza automáticamente la generación del informe final mediante `generar_informe.py`.

Al finalizar la ejecución, se genera el fichero:

`Informe_Final_Riesgos_Multidominio.pdf`

## Resultado esperado

Durante la ejecución de `motor_difuso.py`, la terminal muestra los valores globales de riesgo inherente y residual para las misiones del caso de uso. Además, se genera un informe PDF con:

- evaluación global de la misión;
- nodos de atención prioritaria;
- amenazas detectadas en activos;
- estado completo de la red jerárquica.


## Notas

Si se desea comprobar la generación de los ficheros de salida, pueden eliminarse previamente `ontologia_poblada.rdf` e `Informe_Final_Riesgos_Multidominio.pdf`. Al ejecutar de nuevo `poblar_desde_json.py` y `motor_difuso.py`, el sistema volverá a generar la ontología poblada y el informe PDF final.
