import streamlit as st
from google import genai
from google.genai.errors import APIError
import os
import datetime

# --- A. CONFIGURACIÓN VISUAL (Tematización Dinámica) ---

# Paletas de Colores
PALETA_CLARA = {
    "fondo_principal": "#FFFFFF",
    "fondo_secundario": "#F8F9FA",
    "texto": "#343A40",
    "acento": "#007BFF", # Azul Eficiencia
    "acento_tabla": "#007BFF"
}

PALETA_OSCURA = {
    "fondo_principal": "#121212",
    "fondo_secundario": "#1E1E1E",
    "texto": "#FFFFFF",
    "acento": "#BB86FC", # Púrpura/Azul Acero
    "acento_tabla": "#BB86FC"
}

# Configuración de la página
st.set_page_config(
    page_title="Planificador Dinámico IA",
    page_icon="🗓️",
    layout="centered",
    initial_sidebar_state="auto"
)

# 1. Selector de Tema en la Barra Lateral
with st.sidebar:
    st.header("Ajustes de Tema")
    theme_choice = st.selectbox("Elige un Modo:", ["Modo Claro ☀️", "Modo Oscuro 🌑"])

# 2. Asignación de Paleta
if theme_choice == "Modo Claro ☀️":
    PALETA = PALETA_CLARA
else:
    PALETA = PALETA_OSCURA

# 3. Inyección de CSS (Asegura la adaptabilidad)
dynamic_css = f"""
<style>
/* 1. Fondo principal y texto general */
.stApp {{
    background-color: {PALETA['fondo_principal']}; 
    color: {PALETA['texto']} !important;
}}
/* 2. Contenedores y Expander (elementos tipo "tarjeta") */
.stContainer, .stExpander, div[data-testid="stExpander"] {{
    background-color: {PALETA['fondo_secundario']} !important; 
    border-radius: 10px; 
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); 
    padding: 20px;
}}
/* 3. Títulos, Labels y texto */
h1, h2, h3, h4, label, p, .stMarkdown, .st-ag {{
    color: {PALETA['texto']} !important;
}}
/* 4. Estilo de los encabezados de la tabla generada por la IA */
table th {{
    background-color: {PALETA['acento_tabla']}; 
    color: {PALETA_CLARA['texto']} !important; /* Siempre negro/oscuro para buen contraste en el encabezado */
}}
/* 5. Inputs y selectores de fondo */
div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, div[data-baseweb="textarea"] > div {{
    background-color: {PALETA['fondo_principal']} !important;
    border-color: {PALETA['texto']}20 !important; /* Borde suave */
    color: {PALETA['texto']} !important;
}}
</style>
"""
st.markdown(dynamic_css, unsafe_allow_html=True)


# --- B. LÓGICA DE LA APLICACIÓN ---

# Inicialización del cliente de Gemini
try:
    client = genai.Client()
except Exception:
    st.error("🚨 La clave GEMINI_API_KEY no está configurada. Por favor, revisa los secretos de tu plataforma de hosting.")
    st.stop() 

MODEL_NAME = 'gemini-2.5-flash'

# --- 1. PROMPT MAESTRO (INCLUYE ANÁLISIS DE TÉCNICA) ---
def ensamblar_prompt_multi(task_list_text, horas_disponibles, mejor_momento):
    """Ensambla el prompt con la lógica de Cadena de Pensamiento (CoT) y la recomendación de técnica."""
    return f"""
Actúa como un Experto en Planificación y Optimización de Procesos Académicos. Tu objetivo es crear un plan de estudio semanal que optimice la eficiencia y minimice el estrés para el estudiante.

**DATOS DE ENTRADA:**
- Horas de Estudio Diarias Disponibles: {horas_disponibles} horas.
- Mejor Momento de Productividad: {mejor_momento}.
- LISTA DE TAREAS Y REQUERIMIENTOS:
{task_list_text}

**APLICACIÓN DE INGENIERÍA DE PROCESOS (CoT):**
1. Evalúa la Criticidad (Dificultad + Fecha Límite + Energía) de CADA tarea.
2. Prioriza las tareas con la Fecha Límite más cercana Y la Dificultad más alta.
3. Asigna bloques de 1.5 a 2 horas, poniendo los bloques más difíciles en el {mejor_momento}.

**RESTRICCIÓN:** No excedas el límite de {horas_disponibles} horas diarias.

**OUTPUT REQUERIDO:**
1. Genera un plan de estudio DÍA POR DÍA para la próxima semana en formato **Tabla Markdown**. La tabla debe tener las columnas: Día, Tarea (Nombre y Fecha Límite), Horario, Enfoque (Bloque de 1.5-2h).
2. **NUEVO FACTOR SORPRESA:** Después de la tabla, proporciona un 'Asesoramiento de Productividad' con el siguiente formato:
    * **Técnica Recomendada:** [Nombre de la técnica, ej: Pomodoro, Feynman, Repetición Espaciada]
    * **Justificación de Uso:** [Una explicación de 2 líneas sobre por qué esta técnica es ideal para el momento del día ({mejor_momento}) y el tipo de tareas.]
3. Finaliza con un 'Comentario Crítico' de no más de 3 líneas.
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

# --- C. INTERFAZ DE STREAMLIT (Con Estilo Dinámico) ---

st.title("🗓️ Planificador Dinámico con IA")
st.markdown("Optimiza tu tiempo de estudio con un plan semanal basado en tus recursos y la dificultad de tus tareas.")

# Inicializar lista de tareas
if 'tasks' not in st.session_state:
    st.session_state.tasks = [{'id': 1}]

def add_task():
    st.session_state.tasks.append({'id': len(st.session_state.tasks) + 1})

# Recopilación de datos generales
with st.expander("Recursos y Horarios", expanded=True):
    col_horas, col_momento = st.columns(2)
    with col_horas:
        horas_disponibles = st.number_input("⏰ Horas de Estudio Diarias Disponibles:", min_value=1, value=3, help="Máximo de horas que puedes dedicar por día.")
    with col_momento:
        mejor_momento = st.selectbox("⚡ Mejor Momento del Día (Pico de Energía):", ["Mañana", "Tarde", "Noche"])


# Recopilación de datos de tareas
task_data = []
st.subheader("📝 Detalles de las Tareas")

for i, task in enumerate(st.session_state.tasks):
    with st.expander(f"Tarea {i+1}", expanded=True):
        col_nombre, col_fecha, col_dificultad, col_energia = st.columns([2, 1, 1, 1])
        
        with col_nombre:
            tarea = st.text_input("Nombre de la Tarea:", key=f'tarea_{i}', value=f"Tarea Pendiente {i+1}")
        with col_fecha:
            fecha_limite = st.date_input("Fecha Límite:", key=f'fechaLimite_{i}', value=datetime.date.today() + datetime.timedelta(days=7))
        with col_dificultad:
            dificultad = st.slider("Dificultad (1-10):", min_value=1, max_value=10, value=5, key=f'dificultad_{i}', help="Impacto cognitivo: 1 (Fácil) a 10 (Muy Difícil).")
        with col_energia:
            energia = st.selectbox("Req. de Energía:", ["Alto", "Medio", "Bajo"], key=f'energia_{i}', help="¿Cuánta energía mental te pide esta tarea?")
            
        task_data.append({
            "tarea": tarea,
            "fechaLimite": str(fecha_limite),
            "dificultad": dificultad,
            "energia": energia
        })

# Botones de gestión de tareas
st.markdown("---")
col_add, col_remove = st.columns([1, 1])
with col_add:
    st.button("➕ Agregar Tarea Adicional", on_click=add_task, use_container_width=True)
with col_remove:
    if st.session_state.tasks and len(st.session_state.tasks) > 1:
        st.button("➖ Eliminar Última Tarea", on_click=lambda: st.session_state.tasks.pop(), use_container_width=True)


# Botón de Ejecución Final
st.markdown("---")
if st.button("🚀 Generar Plan Optimizando", type="primary", use_container_width=True):
    if not task_data:
        st.warning("Por favor, agregue al menos una tarea.")
    else:
        # Construir el texto plano de tareas para el Prompt
        task_list_text = ""
        for i, t in enumerate(task_data):
            task_list_text += f"Tarea {i + 1}: {t['tarea']} (Límite: {t['fechaLimite']}, Dificultad: {t['dificultad']}/10, Energía: {t['energia']})\n"

        # Ensamblar y Llamar a Gemini
        prompt = ensamblar_prompt_multi(task_list_text, horas_disponibles, mejor_momento)
        
        with st.spinner('✨ Cargando... Generando la estrategia óptima con IA. Esto puede tardar unos segundos.'):
            resultado_ia = llamar_gemini(prompt)

        # Mostrar Resultado
        if resultado_ia:
            st.header("📋 Plan de Estudio Generado")
            st.success("✅ Planificación Generada con Éxito") 
            st.markdown(resultado_ia)
