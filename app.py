import streamlit as st
from google import genai
from google.genai.errors import APIError
import os

# --- 0. CONFIGURACIÓN INICIAL Y CLAVE API ---
# El cliente de Gemini leerá la clave de las variables de entorno de la plataforma de hosting.
try:
    # Asegúrate de que GEMINI_API_KEY esté configurada como variable de entorno o secreto.
    client = genai.Client() 
except Exception:
    st.error("🚨 La clave GEMINI_API_KEY no está configurada. Por favor, revisa los secretos de tu plataforma de hosting (Streamlit Cloud).")
    st.stop() 

MODEL_NAME = 'gemini-2.5-flash'

# --- 1. PROMPT MAESTRO (CoT) ---
def ensamblar_prompt_multi(task_list_text, horas_disponibles, mejor_momento):
    """Ensambla el prompt con la lógica de Cadena de Pensamiento (CoT)."""
    return f"""
Actúa como un Experto en Planificación y Optimización de Procesos Académicos. Tu objetivo es crear un plan de estudio semanal que optimice la eficiencia y minimice el estrés para el estudiante.

**DATOS DE ENTRADA:**
- Horas de Estudio Diarias Disponibles: {horas_disponibles} horas.
- Mejor Momento de Productividad: {mejor_momento}.
- LISTA DE TAREAS Y REQUERIMIENTOS:
{task_list_text}

**APLICACIÓN DE INGENIERÍA DE PROCESOS (CoT):**
1. Evalúa la Criticidad (Dificultad + Fecha Límite + Energía) de CADA tarea.
2. Prioriza las tareas más Críticas.
3. Asigna bloques de 1.5 a 2 horas, poniendo los bloques más difíciles en el {mejor_momento}.

**RESTRICCIÓN:** No excedas el límite de {horas_disponibles} horas diarias.

**OUTPUT REQUERIDO:**
1. Genera un plan de estudio DÍA POR DÍA para la próxima semana en formato **Tabla Markdown**. La tabla debe tener las columnas: Día, Tarea (Nombre y Fecha Límite), Horario, Enfoque (Bloque de 1.5-2h).
2. Después de la tabla, proporciona un 'Comentario Crítico' de no más de 3 líneas.
"""

# --- 2. FUNCIÓN DE LLAMADA A LA API ---
@st.cache_data(show_spinner=False)
def llamar_gemini(prompt):
    """Llama a la API de Gemini y maneja los errores."""
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={"temperature": 0.5}
        )
        return response.text

    except APIError as e:
        st.error(f"🚨 Error de API de Gemini: {e}")
        return None
    except Exception as e:
        st.error(f"🚨 Error inesperado: {e}")
        return None

# --- 3. INTERFAZ DE STREAMLIT ---

st.set_page_config(page_title="Planificador Dinámico", layout="centered")
st.title("🗓️ Planificador Dinámico con IA")

# Inicializar lista de tareas
if 'tasks' not in st.session_state:
    st.session_state.tasks = [{'id': 1}]

def add_task():
    st.session_state.tasks.append({'id': len(st.session_state.tasks) + 1})

# Recopilación de datos de tareas
task_data = []
with st.container(border=True):
    st.subheader("Entrada de Tareas")
    
    for i, task in enumerate(st.session_state.tasks):
        st.markdown(f"#### Tarea {i+1}")
        
        tarea = st.text_input("Nombre:", key=f'tarea_{i}', value=f"Tarea {i+1}")
        fecha_limite = st.date_input("Fecha Límite:", key=f'fechaLimite_{i}')
        dificultad = st.slider("Dificultad (1-10):", min_value=1, max_value=10, value=5, key=f'dificultad_{i}')
        energia = st.selectbox("Requerimiento de Energía:", ["Alto", "Medio", "Bajo"], key=f'energia_{i}')
        
        task_data.append({
            "tarea": tarea,
            "fechaLimite": str(fecha_limite),
            "dificultad": dificultad,
            "energia": energia
        })

    # Botones de gestión de tareas
    col_add, col_remove = st.columns([1, 1])
    with col_add:
        st.button("+ Agregar Tarea Adicional", on_click=add_task)
    with col_remove:
        # Permite eliminar la última tarea si hay más de una
        if st.session_state.tasks and len(st.session_state.tasks) > 1:
            st.button("➖ Eliminar Última Tarea", on_click=lambda: st.session_state.tasks.pop())


# Recolección de datos generales
with st.container(border=True):
    st.subheader("Recursos Personales")
    horas_disponibles = st.number_input("Horas de Estudio Diarias Disponibles:", min_value=1, value=3)
    mejor_momento = st.selectbox("Mejor Momento del Día:", ["Mañana", "Tarde", "Noche"])


# Botón de Ejecución Final
if st.button("🚀 Generar Plan Optimizando"):
    if not task_data:
        st.warning("Por favor, agregue al menos una tarea.")
    else:
        # Construir el texto plano de tareas para el Prompt
        task_list_text = ""
        for i, t in enumerate(task_data):
            task_list_text += f"Tarea {i + 1}: {t['tarea']} (Límite: {t['fechaLimite']}, Dificultad: {t['dificultad']}/10, Energía: {t['energia']})\n"

        # Ensamblar y Llamar a Gemini
        prompt = ensamblar_prompt_multi(task_list_text, horas_disponibles, mejor_momento)
        
        with st.spinner('Cargando... Generando plan con IA. Esto puede tardar unos segundos.'):
            resultado_ia = llamar_gemini(prompt)

        # Mostrar Resultado
        if resultado_ia:
            st.success("✅ Planificación Generada con Éxito")
            st.markdown("---")
            st.markdown(resultado_ia) # Streamlit renderiza el Markdown
