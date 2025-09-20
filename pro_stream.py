import streamlit as st
import pandas as pd
from mplsoccer import Pitch

st.title("Excursionistas 2025 ⚽")

# Barra lateral - Navegación
# Escudo de Excursionistas (centrado)
col1, col2, col3 = st.sidebar.columns([1, 2, 1])
with col2:
    st.image("Club_Atletico_Excursionistas.svg.png", width=100)

# Botones de navegación
if st.sidebar.button("Análisis de equipo", use_container_width=True):
    st.session_state.page = "equipo"

if st.sidebar.button("Análisis individual", use_container_width=True):
    st.session_state.page = "individual"

# Firma del analista
st.sidebar.markdown("---")
st.sidebar.markdown("**Analista:** Cristian Aragón")

# Inicializar página si no existe
if 'page' not in st.session_state:
    st.session_state.page = "individual"

# Cargar datos de ambos partidos
df_italiano = pd.read_csv("sportivo italiano.csv", sep=';')
df_midland = pd.read_csv("Midland.csv", sep=';')

# Agregar columna de partido
df_italiano['Partido'] = 'Sportivo Italiano'
df_midland['Partido'] = 'Midland'

# Combinar ambos DataFrames
df = pd.concat([df_italiano, df_midland], ignore_index=True)
passes = df[df["Event"].isin(["PB","PM"])].copy()

# Página de Análisis Individual
if st.session_state.page == "individual":
    st.subheader("Análisis Individual")
    
    # Filtros en la página principal
    col1, col2 = st.columns(2)
    with col1:
        partido = st.selectbox("Seleccionar partido", sorted(passes["Partido"].unique()))
    
    # Filtrar pases por partido seleccionado
    passes_partido = passes[passes['Partido'] == partido]
    
    with col2:
        player = st.selectbox("Seleccionar jugador", sorted(passes_partido["Player"].unique()))

    # Función para plotear pases
    def plot_passes(df, ax, pitch):
        for x in df.to_dict(orient="records"):
            x_start, y_start = x['X'], x['Y']  # inicio
            x_end, y_end = x['X2'], x['Y2'] # fin
            color = 'green' if x['Event'] == 'PB' else 'red'

            # Aplicar transformación de coordenadas (invertir arriba/abajo)
            y_start = 100 - y_start
            y_end = 100 - y_end
            
            pitch.scatter(x_start, y_start, edgecolor=color, facecolor=color, s=10, alpha=0.7, ax=ax)
        
            # Línea/flecha hasta donde termina el pase
            pitch.lines(x_start, y_start, x_end, y_end, comet=True, color=color, lw=4, ax=ax, alpha=0.3)

    # Filtrar pases del jugador seleccionado y limpiar datos
    player_passes = passes_partido[passes_partido['Player'] == player].copy()

    # Limpiar datos: convertir "-" y valores vacíos a NaN, luego eliminar filas con NaN
    player_passes['X'] = pd.to_numeric(player_passes['X'], errors='coerce')
    player_passes['Y'] = pd.to_numeric(player_passes['Y'], errors='coerce')
    player_passes['X2'] = pd.to_numeric(player_passes['X2'], errors='coerce')
    player_passes['Y2'] = pd.to_numeric(player_passes['Y2'], errors='coerce')

    # Eliminar filas donde falten coordenadas
    player_passes = player_passes.dropna(subset=['X', 'Y', 'X2', 'Y2'])

    # Contar pases del jugador seleccionado
    num_correct_passes = player_passes[player_passes['Event'] == 'PB'].shape[0]
    num_incorrect_passes = player_passes[player_passes['Event'] == 'PM'].shape[0]

    # Crear el plot
    pitch = Pitch(pitch_type='opta')
    fig, ax = pitch.draw(figsize=(6, 4))
    plot_passes(player_passes, ax, pitch)

    # Mostrar estadísticas del partido seleccionado
    st.markdown("---")
    st.subheader(f"Estadísticas de {player} vs {partido}")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Pases Correctos", num_correct_passes, delta=None)
    with col2:
        st.metric("Pases Incorrectos", num_incorrect_passes, delta=None)

    # Mostrar el plot
    st.pyplot(fig)
    
    # Estadísticas generales (todos los partidos) - Debajo del campo
    st.markdown("---")
    st.subheader("Estadísticas Generales")
    
    # Filtrar pases del jugador en todos los partidos
    player_all_passes = passes[passes['Player'] == player].copy()
    
    # Limpiar datos para estadísticas generales
    player_all_passes['X'] = pd.to_numeric(player_all_passes['X'], errors='coerce')
    player_all_passes['Y'] = pd.to_numeric(player_all_passes['Y'], errors='coerce')
    player_all_passes['X2'] = pd.to_numeric(player_all_passes['X2'], errors='coerce')
    player_all_passes['Y2'] = pd.to_numeric(player_all_passes['Y2'], errors='coerce')
    player_all_passes = player_all_passes.dropna(subset=['X', 'Y', 'X2', 'Y2'])
    
    # Calcular estadísticas generales
    total_correct = player_all_passes[player_all_passes['Event'] == 'PB'].shape[0]
    total_incorrect = player_all_passes[player_all_passes['Event'] == 'PM'].shape[0]
    total_passes = total_correct + total_incorrect
    accuracy_percentage = (total_correct / total_passes * 100) if total_passes > 0 else 0
    
    # Mostrar estadísticas generales
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Pases Correctos", f"{total_correct}/{total_passes}")
    with col2:
        st.metric("Precisión", f"{accuracy_percentage:.1f}%")
    with col3:
        st.metric("Partidos Jugados", len(player_all_passes['Partido'].unique()))

# Página de Análisis de Equipo
elif st.session_state.page == "equipo":
    st.subheader("Análisis de Equipo")
    st.info("Laburando...")
    
    
    
    


