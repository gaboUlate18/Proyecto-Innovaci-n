import streamlit as st
from google import genai
from google.genai.errors import APIError
import os
import datetime

# --- A. DICCIONARIO DE TEXTOS (Multilenguaje) ---

TEXTOS = {
    "es": {
        "page_title": "Planificador Dinámico IA",
        "app_title": "🗓️ Planificador Dinámico con IA",
        "app_subtitle": "Optimiza tu tiempo de estudio con un plan semanal basado en tus recursos y la dificultad de tus tareas.",
        "sidebar_header": "⚙️ Ajustes Avanzados",
        "theme_subheader": "🎨 Tema y Visualización",
        "theme_select": "Elige un Modo:",
        "theme_light": "Modo Claro ☀️",
        "theme_dark": "Modo Oscuro 🌑",
        "lang_subheader": "🌐 Idioma",
        "lang_select": "Seleccionar Idioma:",
        "restrictions_subheader": "🗓️ Restricciones de Días",
        "block_checkbox": "Activar Bloqueo de Días Específicos",
        "block_help": "Si se activa, aparecerá una opción en la pantalla principal para seleccionar días libres.",
        "resources_title": "Recursos y Horarios",
        "hours_input": "⏰ Horas de Estudio Diarias Disponibles:",
        "hours_help": "Máximo de horas que puedes dedicar por día.",
        "moment_select": "⚡ Mejor Momento del Día (Pico de Energía):",
        "moment_options": ["Mañana", "Tarde", "Noche"],
        "tasks_subheader": "📝 Detalles de las Tareas",
        "task_name": "Nombre de la Tarea:",
        "task_due": "Fecha Límite:",
        "task_difficulty": "Dificultad (1-10):",
        "difficulty_help": "Impacto cognitivo: 1 (Fácil) a 10 (Muy Difícil).",
        "task_energy": "Req. de Energía:",
        "energy_options": ["Alto", "Medio", "Bajo"],
        "add_task": "➕ Agregar Tarea Adicional",
        "remove_task": "➖ Eliminar Última Tarea",
        "generate_button": "🚀 Generar Plan Optimizando",
        "warning_no_task": "Por favor, agregue al menos una tarea.",
        "spinner_msg": "✨ Cargando... Generando la estrategia óptima con IA. Esto puede tardar unos segundos.",
        "result_header": "📋 Plan de Estudio Generado",
        "result_success": "✅ Planificación Generada con Éxito",
        "block_multiselect": "🚫 ¿Qué días de la semana deseas bloquear completamente para descanso?",
        "block_multiselect_help": "Los días seleccionados serán excluidos de la planificación de tareas.",
        "days": ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'],
        "day_defaults": ['Sábado', 'Domingo'],
        "output_format_radio": "📝 Formato de Plan Generado:", 
        "output_format_options": ["Tabla Markdown", "Texto Plano"],
        "error_api": "🚨 Error de API de Gemini: ",
        "error_unexpected": "🚨 Error inesperado: ",
        "error_key": "🚨 La clave GEMINI_API_KEY no está configurada. Por favor, revisa los secretos de tu plataforma de hosting.",
        "task_placeholder": "Tarea Pendiente "
    },
    "en": {
        "page_title": "Dynamic AI Planner",
        "app_title": "🗓️ Dynamic AI Planner",
        "app_subtitle": "Optimize your study time with a weekly plan based on your resources and task difficulty.",
        "sidebar_header": "⚙️ Advanced Settings",
        "theme_subheader": "🎨 Theme and Visualization",
        "theme_select": "Choose Mode:",
        "theme_light": "Light Mode ☀️",
        "theme_dark": "Dark Mode 🌑",
        "lang_subheader": "🌐 Language",
        "lang_select": "Select Language:",
        "restrictions_subheader": "🗓️ Day Restrictions",
        "block_checkbox": "Activate Specific Day Blocking",
        "block_help": "If activated, an option will appear on the main screen to select free days.",
        "resources_title": "Resources and Schedule",
        "hours_input": "⏰ Daily Study Hours Available:",
        "hours_help": "Maximum hours you can dedicate per day.",
        "moment_select": "⚡ Best Time of Day (Energy Peak):",
        "moment_options": ["Morning", "Afternoon", "Night"],
        "tasks_subheader": "📝 Task Details",
        "task_name": "Task Name:",
        "task_due": "Due Date:",
        "task_difficulty": "Difficulty (1-10):",
        "difficulty_help": "Cognitive impact: 1 (Easy) to 10 (Very Difficult).",
        "task_energy": "Energy Requirement:",
        "energy_options": ["High", "Medium", "Low"],
        "add_task": "➕ Add Additional Task",
        "remove_task": "➖ Remove Last Task",
        "generate_button": "🚀 Generate Optimized Plan",
        "warning_no_task": "Please add at least one task.",
        "spinner_msg": "✨ Loading... Generating the optimal strategy with AI. This may take a few seconds.",
        "result_header": "📋 Generated Study Plan",
        "result_success": "✅ Planning Generated Successfully",
        "block_multiselect": "🚫 Which days of the week do you want to completely block for rest?",
        "block_multiselect_help": "Selected days will be excluded from task planning.",
        "days": ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        "day_defaults": ['Saturday', 'Sunday'],
        "output_format_radio": "📝 Generated Plan Format:",
        "output_format_options": ["Markdown Table", "Plain Text"],
        "error_api": "🚨 Gemini API Error: ",
        "error_unexpected": "🚨 Unexpected Error: ",
        "error_key": "🚨 The GEMINI_API_KEY is not configured. Please check your hosting platform secrets.",
        "task_placeholder": "Pending Task "
    }
}

# --- B. CONFIGURACIÓN VISUAL (Tematización Dinámica) ---

PALETA_CLARA = {
    "fondo_principal": "#FFFFFF",
    "fondo_secundario": "#F8F9FA",
    "texto_general": "#343A40",        
    "texto_acento": "#007BFF",         
    "acento_tabla": "#007BFF"          
}

PALETA_OSCURA = {
    "fondo_principal": "#121212",
    "fondo_secundario": "#1E1E1E",
    "texto_general": "#FFFFFF",        
    "texto_acento": "#BB86FC",         
    "acento_tabla": "#BB86FC"          
}

st.set_page_config(
    page_title=TEXTOS["es"]["page_title"], 
    page_icon="🗓️",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- C. BARRA LATERAL (st.sidebar) ---

# Se inicializa el estado de la aplicación
if 'resultado_ia_raw' not in st.session_state:
    st.session_state.resultado_ia_raw = None
if 'idioma' not in st.session_state:
    st.session_state.idioma = 'es'

with st.sidebar:
    st.header(TEXTOS["es"]["sidebar_header"]) 

    ## 0. SELECTOR DE IDIOMA
    st.subheader(TEXTOS["es"]["lang_subheader"])
    idioma_map = {"Español": "es", "English": "en"}
    idioma_seleccionado = st.selectbox(
        TEXTOS["es"]["lang_select"],
        options=list(idioma_map.keys()),
        index=0,
        key="language_selector"
    )
    st.session_state.idioma = idioma_map[idioma_seleccionado]
    T = TEXTOS[st.session_state.idioma] # Asignamos el diccionario de textos

    st.markdown("---")
    
    ## 1. AJUSTES DE TEMA (Paleta Dinámica)
    st.subheader(T["theme_subheader"])
    theme_choice = st.selectbox(T["theme_select"], [T["theme_light"], T["theme_dark"]])
    st.markdown("---")

    ## 2. RESTRICCIONES DE DÍAS
    st.subheader(T["restrictions_subheader"])
    activar_bloqueo_dias = st.checkbox(
        T["block_checkbox"],
        help=T["block_help"]
    )
    # st.markdown("---") <-- ESTE FUE ELIMINADO
    
# --- FIN DE BARRA LATERAL ---

# 4. Lógica de Temas y CSS

# Asignación de Paleta de Tema (Basado en la selección del sidebar)
if theme_choice == T["theme_light"]:
    PALETA = PALETA_CLARA
else:
    PALETA = PALETA_OSCURA

# 5. Inyección de CSS (INCLUYE OVERRIDE PARA TEXTO BLANCO EN MODO CLARO)
white_text_override = ""
if theme_choice == T["theme_light"]:
    # Forzar color blanco para etiquetas en la barra lateral cuando el fondo de la app es claro
    white_text_override = """
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stButton > button {
        color: white !important;
    }
    """

dynamic_css = f"""
<style>
/* Estilos generales */
.stApp {{ background-color: {PALETA['fondo_principal']}; }}
.stContainer, .stExpander, div[data-testid="stExpander"] {{
    background-color: {PALETA['fondo_secundario']} !important; 
    border-radius: 10px; 
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); 
    padding: 20px;
}}
h1, h2, h3, h4 {{ color: {PALETA['texto_acento']} !important; }}
/* Color general de etiquetas y texto */
label, p, .stMarkdown, .st-ag {{ color: {PALETA['texto_general']} !important; }}
table th {{ background-color: {PALETA['acento_tabla']}; color: {PALETA_CLARA['fondo_principal']} !important; }}
div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, div[data-baseweb="textarea"] > div, div[data-testid="stExpander"] > div:first-child {{
    background-color: {PALETA['fondo_principal']} !important;
    border-color: {PALETA['texto_general']}20 !important; 
    color: {PALETA['texto_general']} !important;
}}
/* Botón principal */
button.stButton > div > button[kind="primary"] {{
    color: {PALETA_CLARA['fondo_principal']} !important; 
}}

{white_text_override} /* Inyección del CSS condicional */
</style>
"""
st.markdown(dynamic_css, unsafe_allow_html=True)


# --- E. FUNCIONES DE LÓGICA (Se usa T para textos) ---

# Variable de temperatura fijada
ia_temperature = 0.5 

# Inicialización del cliente de Gemini
try:
    client = genai.Client()
except Exception:
    st.error(T["error_key"])
    st.stop() 

MODEL_NAME = 'gemini-2.5-flash'


# --- 1. PROMPT MAESTRO ---
def ensamblar_prompt_multi(task_list_text, horas_disponibles, mejor_momento, dias_bloqueados, idioma):
    """Ensambla el prompt con la lógica de CoT, restricciones y formato de salida."""
    
    dias_bloqueados_str = ", ".join(dias_bloqueados)
    
    # Textos clave que cambian para el Prompt
    if idioma == 'en':
        prompt_language = "English"
        restraint_text = f"Restraint: You MUST NOT assign NEW tasks or focus activities on the following days: {dias_bloqueados_str}."
        output_format_text = "Generate a day-by-day study plan for the next week in standard **Markdown Table** format. The table must have exactly the columns: Day, Task (Name and Due Date), Schedule, Focus (1.5-2h Block)."
    else: # español
        prompt_language = "Español"
        restraint_text = f"Restricción de Días: NO debes asignar **NUEVAS** tareas ni actividades de enfoque los días: {dias_bloqueados_str}."
        output_format_text = "Genera un plan de estudio DÍA POR DÍA para la próxima semana en formato **Tabla Markdown estándar**. La tabla debe tener exactamente las columnas: Día, Tarea (Nombre y Fecha Límite), Horario, Enfoque (Bloque de 1.5-2h)."


    return f"""
Actúa como un Experto en Planificación y Optimización de Procesos Académicos. Tu respuesta debe estar completamente en **{prompt_language}**. Tu objetivo es crear un plan de estudio semanal que optimice la eficiencia y minimice el estrés para el estudiante.

**DATOS DE ENTRADA:**
- Horas de Estudio Diarias Disponibles: {horas_disponibles} horas.
- Mejor Momento de Productividad: {mejor_momento}.
- LISTA DE TAREAS Y REQUERIMIENTOS:
{task_list_text}

**RESTRICCIONES Y REGLAS DE PROCESO (CoT):**
1. {restraint_text}
2. Evalúa la Criticidad (Dificultad + Fecha Límite + Energía) de CADA tarea.
3. Prioriza las tareas con la Fecha Límite más cercana Y la Dificultad más alta.
4. Asigna bloques de 1.5 a 2 horas, poniendo los bloques más difíciles en el {mejor_momento}.
5. Restricción de Horas: No excedas el límite de {horas_disponibles} horas diarias.

**OUTPUT REQUERIDO:**
1. {output_format_text}
2. Después del plan, proporciona un 'Asesoramiento de Productividad' con el siguiente formato, utilizando los términos en **{prompt_language}**:
    * Técnica Recomendada: [Nombre de la técnica]
    * Justificación de Uso: [Una explicación de 2 líneas]
3. Finaliza con un 'Comentario Crítico' de no más de 3 líneas en **{prompt_language}**.
"""

# --- 2. FUNCIÓN DE LLAMADA A LA API ---
@st.cache_data(show_spinner=False)
def llamar_gemini(prompt, temperature):
    """Llama a la API de Gemini y maneja los errores."""
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={"temperature": temperature}
        )
        return response.text

    except APIError as e:
        st.error(T["error_api"] + str(e))
        return None
    except Exception as e:
        st.error(T["error_unexpected"] + str(e))
        return None

# --- F. INTERFAZ PRINCIPAL DE STREAMLIT ---

st.title(T["app_title"])
st.markdown(T["app_subtitle"])

# Inicializar lista de tareas
if 'tasks' not in st.session_state:
    st.session_state.tasks = [{'id': 1}]

def add_task():
    st.session_state.tasks.append({'id': len(st.session_state.tasks) + 1})

# Recopilación de datos generales
with st.expander(T["resources_title"], expanded=True):
    col_horas, col_momento = st.columns(2)
    with col_horas:
        horas_disponibles = st.number_input(T["hours_input"], min_value=1, value=3, help=T["hours_help"])
    with col_momento:
        mejor_momento = st.selectbox(T["moment_select"], T["moment_options"])
    
    # --- LÓGICA CONDICIONAL DE DÍAS BLOQUEADOS ---
    dias_bloqueados = []

    if activar_bloqueo_dias:
        st.markdown("---")
        st.subheader(T["restrictions_subheader"])
        dias_bloqueados = st.multiselect(
            T["block_multiselect"], 
            T["days"],
            default=T["day_defaults"],
            help=T["block_multiselect_help"]
        )
    else:
        dias_bloqueados = []
        

# Recopilación de datos de tareas
task_data = []
st.subheader(T["tasks_subheader"])

for i, task in enumerate(st.session_state.tasks):
    with st.expander(f"{T['task_placeholder']} {i+1}", expanded=True):
        col_nombre, col_fecha, col_dificultad, col_energia = st.columns([2, 1, 1, 1])
        
        with col_nombre:
            tarea = st.text_input(T["task_name"], key=f'tarea_{i}', value=f"{T['task_placeholder']} {i+1}")
        with col_fecha:
            fecha_limite = st.date_input(T["task_due"], key=f'fechaLimite_{i}', value=datetime.date.today() + datetime.timedelta(days=7))
        with col_dificultad:
            dificultad = st.slider(T["task_difficulty"], min_value=1, max_value=10, value=5, key=f'dificultad_{i}', help=T["difficulty_help"])
        with col_energia:
            energia = st.selectbox(T["task_energy"], T["energy_options"], key=f'energia_{i}')
            
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
    st.button(T["add_task"], on_click=add_task, use_container_width=True)
with col_remove:
    if st.session_state.tasks and len(st.session_state.tasks) > 1:
        st.button(T["remove_task"], on_click=lambda: st.session_state.tasks.pop(), use_container_width=True)


# Botón de Ejecución Final
st.markdown("---")
if st.button(T["generate_button"], type="primary", use_container_width=True):
    if not task_data:
        st.warning(T["warning_no_task"])
    else:
        # Construir el texto plano de tareas para el Prompt
        task_list_text = ""
        for i, t in enumerate(task_data):
            task_list_text += f"Tarea {i + 1}: {t['tarea']} (Límite: {t['fechaLimite']}, Dificultad: {t['dificultad']}/10, Energía: {t['energia']})\n"

        # Ensamblar y Llamar a Gemini con la temperatura fija: ia_temperature = 0.5
        prompt = ensamblar_prompt_multi(task_list_text, horas_disponibles, mejor_momento, dias_bloqueados, st.session_state.idioma)
        
        with st.spinner(T["spinner_msg"]):
            resultado_ia = llamar_gemini(prompt, ia_temperature) 

        # Mostrar Resultado
        if resultado_ia:
            st.header(T["result_header"])
            st.success(T["result_success"]) 
            
            st.markdown("---")
            st.markdown(resultado_ia)
            
            st.session_state.resultado_ia_raw = resultado_ia
