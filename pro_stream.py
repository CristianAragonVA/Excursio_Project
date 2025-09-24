import streamlit as st
import pandas as pd
import numpy as np
from mplsoccer import Pitch
from matplotlib.colors import to_rgba

st.title("Reserva - Excursionistas 2025 ⚽")

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

if st.sidebar.button("Estadísticas generales", use_container_width=True):
    st.session_state.page = "estadisticas"

# Firma del analista
st.sidebar.markdown("---")
st.sidebar.markdown("**Analista:** Cristian Aragón")

# Inicializar página si no existe
if 'page' not in st.session_state:
    st.session_state.page = "equipo"

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
            x_end, y_end = x['X2'], x['Y2']    # fin
            color = 'green' if x['Event'] == 'PB' else 'red'

            # Aplicar transformación de coordenadas (invertir arriba/abajo)
            y_start = 100 - y_start
            y_end = 100 - y_end

            # Flechas (sin comet) y con alpha según tipo de pase
            alpha_val = 0.6 if x['Event'] == 'PB' else 0.2  # menos opacidad en malos
            pitch.arrows(
                x_start, y_start, x_end, y_end,
                color=color, width=2, headwidth=4,
                headlength=5, ax=ax, alpha=alpha_val
            )


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

    # Filtrar todos los eventos del jugador en todos los partidos
    player_all_events = df[df['Player'] == player].copy()

    # --- Dibujar recuperaciones y pérdidas ---
    # Filtrar eventos del jugador
    recuperaciones = player_all_events[player_all_events['Event'] == 'Recuperacion'].copy()
    perdidas = player_all_events[player_all_events['Event'] == 'Perdida'].copy()

    # Limpiar coordenadas
    for df_temp in [recuperaciones, perdidas]:
        df_temp['X'] = pd.to_numeric(df_temp['X'], errors='coerce')
        df_temp['Y'] = pd.to_numeric(df_temp['Y'], errors='coerce')
        df_temp.dropna(subset=['X', 'Y'], inplace=True)
        # Ajustar coordenadas (invertir arriba/abajo)
        df_temp['Y'] = 100 - df_temp['Y']

    # Graficar recuperaciones (verde) y pérdidas (rojo)
    pitch.scatter(
        recuperaciones['X'], recuperaciones['Y'],
        c="green", s=15, linewidth=0.8, alpha=0.3, ax=ax
    )
    pitch.scatter(
        perdidas['X'], perdidas['Y'],
        c="red", s=15, linewidth=0.8, alpha=0.2, ax=ax
    )

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
    
    # Para estadísticas de pases, limpiar datos de coordenadas
    player_all_passes = player_all_events[player_all_events['Event'].isin(['PB', 'PM'])].copy()
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
    
    # Calcular estadísticas adicionales
    pelotas_recuperadas = player_all_events[player_all_events['Event'] == 'Recuperacion'].shape[0]
    pelotas_perdidas = player_all_events[player_all_events['Event'] == 'Perdida'].shape[0]
    faltas_realizadas = player_all_events[player_all_events['Event'] == 'Falta'].shape[0]
    faltas_recibidas = player_all_events[player_all_events['Event'] == 'Falta recibida'].shape[0]
    total_tiros = player_all_events[player_all_events['Event'] == 'Tiro'].shape[0]
    tiros_al_arco = player_all_events[(player_all_events['Event'] == 'Tiro') & 
                                     (player_all_events['Result'].str.contains('Arco|Gol', na=False))].shape[0]
    goles = player_all_events[(player_all_events['Event'] == 'Tiro') & 
                             (player_all_events['Result'].str.contains('Gol', na=False))].shape[0]
    partidos_jugados = len(player_all_events['Partido'].unique())
    
    # Mostrar estadísticas generales - Primera fila: Pases
    st.markdown("#### Pases")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Pases totales", f"{total_correct}/{total_passes}")
    with col2:
        st.metric("Precisión", f"{accuracy_percentage:.1f}%")
    with col3:
        st.metric("Partidos Jugados", partidos_jugados)
    
    # Segunda fila: Tiros
    st.markdown("#### Tiros")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Tiros totales", f"{tiros_al_arco}/{total_tiros}")
    with col2:
        st.metric("Goles", goles)
    
    # Tercera fila: Pelotas recuperadas y perdidas
    st.markdown("#### Posesión")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Pelotas recuperadas", pelotas_recuperadas)
    with col2:
        st.metric("Pelotas perdidas", pelotas_perdidas)
    
    # Cuarta fila: Faltas
    st.markdown("#### Faltas")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Faltas Realizadas", faltas_realizadas)
    with col2:
        st.metric("Faltas Recibidas", faltas_recibidas)
    
    
# Página de Estadísticas Generales
elif st.session_state.page == "estadisticas":
    st.subheader("Estadísticas Generales")
    
    # Calcular estadísticas para todos los jugadores
    def calcular_estadisticas_jugador(player_name):
        player_events = df[df['Player'] == player_name]
        
        # Pases
        pases_correctos = player_events[player_events['Event'] == 'PB'].shape[0]
        pases_incorrectos = player_events[player_events['Event'] == 'PM'].shape[0]
        total_pases = pases_correctos + pases_incorrectos
        porcentaje_pases = (pases_correctos / total_pases * 100) if total_pases > 0 else 0
        
        # Tiros y goles
        total_tiros = player_events[player_events['Event'] == 'Tiro'].shape[0]
        tiros_al_arco = player_events[(player_events['Event'] == 'Tiro') & 
                                     (player_events['Result'].str.contains('Arco|Gol', na=False))].shape[0]
        goles = player_events[(player_events['Event'] == 'Tiro') & 
                             (player_events['Result'].str.contains('Gol', na=False))].shape[0]
        
        # Recuperaciones
        pelotas_recuperadas = player_events[player_events['Event'] == 'Recuperacion'].shape[0]
        
        # Partidos jugados
        partidos_jugados = len(player_events['Partido'].unique())
        
        return {
            'jugador': player_name,
            'pases_correctos': pases_correctos,
            'total_pases': total_pases,
            'porcentaje_pases': porcentaje_pases,
            'total_tiros': total_tiros,
            'tiros_al_arco': tiros_al_arco,
            'goles': goles,
            'pelotas_recuperadas': pelotas_recuperadas,
            'partidos_jugados': partidos_jugados
        }
    
    # Obtener todos los jugadores únicos
    jugadores_unicos = df['Player'].unique()
    
    # Calcular estadísticas para cada jugador
    estadisticas_jugadores = []
    for jugador in jugadores_unicos:
        if jugador and jugador != '-':  # Filtrar valores nulos o vacíos
            stats = calcular_estadisticas_jugador(jugador)
            estadisticas_jugadores.append(stats)
    
    # Convertir a DataFrame
    df_stats = pd.DataFrame(estadisticas_jugadores)
    
    # Tabla 1: Eficacia (Top 5 por mayor porcentaje de pases correctos)
    st.markdown("### 🎯 Eficacia")
    df_eficacia = df_stats.nlargest(5, 'porcentaje_pases')[['jugador', 'total_pases', 'pases_correctos', 'porcentaje_pases']].copy()
    df_eficacia['pases_totales'] = df_eficacia.apply(lambda x: f"{x['pases_correctos']}/{x['total_pases']}", axis=1)
    df_eficacia['%_pases_correctos'] = df_eficacia['porcentaje_pases'].round(1).astype(str) + '%'
    df_eficacia_display = df_eficacia[['jugador', 'pases_totales', '%_pases_correctos']].copy()
    df_eficacia_display.columns = ['Jugador', 'Pases totales', '% Pases correctos']
    st.dataframe(df_eficacia_display, use_container_width=True)
    
    # Tabla 2: Goleadores (Top 5 goles)
    st.markdown("### ⚽ Goleadores")
    df_goleadores = df_stats.nlargest(5, 'goles')[['jugador', 'total_tiros', 'tiros_al_arco', 'goles', 'partidos_jugados']].copy()
    df_goleadores['tiros_totales'] = df_goleadores.apply(lambda x: f"{x['tiros_al_arco']}/{x['total_tiros']}", axis=1)
    df_goleadores['goles_por_partido'] = (df_goleadores['goles'] / df_goleadores['partidos_jugados']).round(2)
    df_goleadores_display = df_goleadores[['jugador', 'tiros_totales', 'goles', 'goles_por_partido']].copy()
    df_goleadores_display.columns = ['Jugador', 'Tiros totales', 'Goles', 'Goles/Partido']
    st.dataframe(df_goleadores_display, use_container_width=True)
    
    # Tabla 3: Defensa (Top 5 recuperaciones)
    st.markdown("### 🛡️ Defensa")
    df_defensa = df_stats.nlargest(5, 'pelotas_recuperadas')[['jugador', 'pelotas_recuperadas']].copy()
    df_defensa.columns = ['Jugador', 'Pelotas recuperadas']
    st.dataframe(df_defensa, use_container_width=True)

# Página de Análisis de Equipo
elif st.session_state.page == "equipo":
    st.subheader("Análisis de Equipo")
    
    # Filtro de rival
    rival = st.selectbox("Seleccionar rival", sorted(df["Partido"].unique()))
    
    # Filtrar datos por rival seleccionado
    df_rival = df[df["Partido"] == rival].copy()
    
    if not df_rival.empty:
        st.markdown(f"### Red de Pases vs {rival}")
        
        # --- 3. Filtrar solo pases completados para la red ---
        passes = df_rival[df_rival["Event"] == "PB"].copy()
        
        if not passes.empty:
            # Limpiar datos de coordenadas
            passes['X'] = pd.to_numeric(passes['X'], errors='coerce')
            passes['Y'] = pd.to_numeric(passes['Y'], errors='coerce')
            passes['X2'] = pd.to_numeric(passes['X2'], errors='coerce')
            passes['Y2'] = pd.to_numeric(passes['Y2'], errors='coerce')
            passes = passes.dropna(subset=['X', 'Y', 'X2', 'Y2'])
            
            # --- 4. Posiciones promedio por jugador ---
            avg_pos = passes.groupby("Player").agg({"X": "mean", "Y": "mean", "recep": "count"}).reset_index()
            avg_pos.rename(columns={"recep": "count"}, inplace=True)
            
            # --- 5. Conteo de pases entre jugadores ---
            pass_counts = passes.groupby(["Player", "recep"]).size().reset_index(name="pass_count")
            pass_counts = pass_counts[pass_counts["pass_count"] > 0]
            
            # --- 6. Merge de posiciones (inicio y fin) ---
            pass_counts = pass_counts.merge(avg_pos, left_on="Player", right_on="Player")
            pass_counts = pass_counts.merge(avg_pos, left_on="recep", right_on="Player", suffixes=["", "_end"])
            
            # --- 7. Orientación cancha ---
            avg_pos["Y"] = 100 - avg_pos["Y"]
            pass_counts["Y"] = 100 - pass_counts["Y"]
            pass_counts["Y_end"] = 100 - pass_counts["Y_end"]
            
            gk_x = avg_pos["X"].min()
            if gk_x > 50:
                avg_pos["X"] = 100 - avg_pos["X"]
                pass_counts["X"] = 100 - pass_counts["X"]
                pass_counts["X_end"] = 100 - pass_counts["X_end"]
                passes["X"] = 100 - passes["X"]  # espejar para heatmap
                passes["Y"] = 100 - passes["Y"]
            
            # --- 8. Estilo de la red ---
            MAX_LINE_WIDTH = 10
            MAX_MARKER_SIZE = 500
            MIN_TRANSPARENCY = 0.1
            
            pass_counts["width"] = (pass_counts.pass_count / pass_counts.pass_count.max()) * MAX_LINE_WIDTH
            
            # Cambiar color de conexiones a verde
            color = np.array(to_rgba("green"))
            color = np.tile(color, (len(pass_counts), 1))
            c_transparency = pass_counts.pass_count / pass_counts.pass_count.max()
            c_transparency = (c_transparency * (1 - MIN_TRANSPARENCY)) + MIN_TRANSPARENCY
            color[:, 3] = c_transparency
            
            avg_pos["marker_size"] = (avg_pos["count"] / avg_pos["count"].max()) * MAX_MARKER_SIZE
            
            # --- 9. Dibujar cancha ---
            pitch = Pitch(pitch_type="opta", line_color="black", pitch_color="white")
            fig, ax = pitch.draw(figsize=(12, 8), constrained_layout=False, tight_layout=True)
            fig.patch.set_facecolor("white")
            ax.set_facecolor("white")
            
            # --- 10. Conexiones ---
            for i, row in pass_counts.iterrows():
                ci = min(i, len(color) - 1)
                pitch.lines(row["X"], row["Y"], row["X_end"], row["Y_end"],
                            ax=ax, color=color[ci], linewidth=row["width"], zorder=2)
            
            # --- 11. Nodos ---
            pitch.scatter(avg_pos.X, avg_pos.Y, ax=ax, color="black", ec="white",
                          s=avg_pos["marker_size"], zorder=3)
            
            for _, r in avg_pos.iterrows():
                ax.text(
                    r.X, r.Y + 2.5, r.Player,
                    color="black", ha="center",
                    fontsize=10, fontweight="bold", zorder=4,
                    bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.3")
                )
            
            # Mostrar el gráfico
            st.pyplot(fig)

            # ========================
            # 🔥 Heatmap Zonal de Pases
            # ========================
            st.markdown("### 🔥 Heatmap Zonal de Pases")

            # Dibujar Heatmap sobre cancha (3x3)
            pitch = Pitch(pitch_type="opta", line_color="black", pitch_color="white")
            fig, ax = pitch.draw(figsize=(8, 6))
            heatmap, xedges, yedges = np.histogram2d(
                passes["X"], passes["Y"], bins=[3, 3], range=[[0, 100], [0, 100]]
            )
            pcm = ax.pcolormesh(xedges, yedges, heatmap.T, cmap="Greens", alpha=0.5)
            fig.colorbar(pcm, ax=ax, shrink=0.7, label="Cantidad de pases")
            st.pyplot(fig)

            # Función para asignar zona 3x3
            def asignar_zona(x, y):
                if x < 33:
                    col = "Salida"
                elif x < 66:
                    col = "Medio"
                else:
                    col = "Último tercio"
                
                if y < 33:
                    fila = "Derecha"
                elif y < 66:
                    fila = "Centro"
                else:
                    fila = "Izquierda"
                return f"{col} - {fila}"

            # Asignar zona de inicio y fin a cada pase
            passes["zona_inicio"] = passes.apply(lambda r: asignar_zona(r["X"], r["Y"]), axis=1)
            passes["zona_fin"] = passes.apply(lambda r: asignar_zona(r["X2"], r["Y2"]), axis=1)

            # Tabla de conteo por zona de inicio
            zonas_count = passes["zona_inicio"].value_counts().reset_index()
            zonas_count.columns = ["Zona", "Pases"]
            st.dataframe(zonas_count, use_container_width=True)
            
            # Estadísticas adicionales
            st.markdown("### Estadísticas del Partido")
            
            # Calcular pases totales (correctos e incorrectos)
            total_pases_correctos = len(passes)
            total_pases_incorrectos = len(df_rival[df_rival["Event"] == "PM"])
            total_pases = total_pases_correctos + total_pases_incorrectos
            
            # Top 3 conexiones de pases
            top_conexiones = pass_counts.nlargest(3, 'pass_count')
            
            # Jugador más participativo (quien dio más pases)
            pases_por_jugador = passes['Player'].value_counts()
            jugador_mas_participativo = pases_por_jugador.index[0] if not pases_por_jugador.empty else "N/A"
            max_pases = pases_por_jugador.iloc[0] if not pases_por_jugador.empty else 0
            
            # Mostrar estadísticas
            st.markdown("#### 📊 Posesión")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Pases totales", f"{total_pases_correctos}/{total_pases}")
            with col2:
                porcentaje_efectividad = (total_pases_correctos / total_pases * 100) if total_pases > 0 else 0
                st.metric("Efectividad", f"{porcentaje_efectividad:.1f}%")
            
            
            # Top 3 conexiones
            st.markdown("#### 🔗 Top 3 Conexiones de Pases")
            for i, (_, row) in enumerate(top_conexiones.iterrows(), 1):
                st.write(f"{i}. **{row['Player']}** → **{row['recep']}**: {row['pass_count']} pases")
            
            # Jugador más participativo
            st.markdown("#### ⭐ Jugador Más Participativo")
            st.write(f"**{jugador_mas_participativo}** con {max_pases} pases")
        else:
            st.warning(f"No hay pases completados registrados para el partido vs {rival}")
    else:
        st.warning("No hay datos disponibles para el rival seleccionado")







