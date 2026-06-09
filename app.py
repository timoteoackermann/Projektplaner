import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Seiteneinstellung für Breitbild (wichtig für Timelines!)
st.set_page_config(layout="wide", page_title="Project Planner (Tom's Clone)", page_icon="📅")

# CSS für das Tom's Planner Design (Clean, moderner Grid-Look)
st.markdown("""
    <style>
    .reportview-container { background: #f5f7f8; }
    h1 { color: #1e293b; font-family: 'Helvetica Neue', sans-serif; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

st.title("📅 Mein Projektplaner")
st.subheader("Frei nach dem Vorbild von Tom's Planner")

# --- INITIALE DATEN (Standard-Template) ---
if 'project_data' not in st.session_state:
    default_data = [
        {"Gruppe": "Konzept", "Aufgabe": "Marktrecherche", "Start": "2026-06-01", "Ende": "2026-06-05", "Status": "Fertig", "Farbe": "#34d399"},
        {"Gruppe": "Konzept", "Aufgabe": "Lastenheft erstellen", "Start": "2026-06-06", "Ende": "2026-06-12", "Status": "In Arbeit", "Farbe": "#38bdf8"},
        {"Gruppe": "Entwicklung", "Aufgabe": "UI Prototyping", "Start": "2026-06-13", "Ende": "2026-06-20", "Status": "Geplant", "Farbe": "#fbbf24"},
        {"Gruppe": "Entwicklung", "Aufgabe": "Backend Setup", "Start": "2026-06-15", "Ende": "2026-06-30", "Status": "Geplant", "Farbe": "#f87171"},
    ]
    st.session_state.project_data = pd.DataFrame(default_data)

df = st.session_state.project_data

# Datentypen für den Editor vorbereiten
df['Start'] = pd.to_datetime(df['Start']).dt.date
df['Ende'] = pd.to_datetime(df['Ende']).dt.date

# --- SIDEBAR: EXPORT & STEUERUNG ---
st.sidebar.header("🛠️ Optionen")
st.sidebar.markdown("Nutze die Tabelle rechts, um Zeilen hinzuzufügen (+ am Tabellenrand) oder zu löschen (Zeile markieren + Entf).")

# CSV Export
csv = df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="📥 Als CSV exportieren",
    data=csv,
    file_name="projektplan.csv",
    mime="text/csv",
)

# Reset Button
if st.sidebar.button("🔄 Plan zurücksetzen"):
    st.session_state.clear()
    st.rerun()

# --- HAUPTBEREICH: TABELLE (Der Editor) ---
st.write("### 📝 Aufgaben-Grid (Direkt editierbar)")

# Konfiguration der Spalten (KORRIGIERT: Ohne fehlerhafte 'required' Parameter)
column_config = {
    "Gruppe": st.column_config.SelectboxColumn("Ordner / Gruppe", options=["Konzept", "Entwicklung", "Design", "Marketing", "QA"]),
    "Aufgabe": st.column_config.TextColumn("Aufgabenname", placeholder="Was ist zu tun?"),
    "Start": st.column_config.DateColumn("Startdatum", format="YYYY-MM-DD"),
    "Ende": st.column_config.DateColumn("Enddatum", format="YYYY-MM-DD"),
    "Status": st.column_config.SelectboxColumn("Status", options=["Geplant", "In Arbeit", "Fertig"]),
    "Farbe": st.column_config.SelectboxColumn("Visualisierung (Farbe)", options=["#34d399", "#38bdf8", "#fbbf24", "#f87171", "#a78bfa"], help="Wähle die Blockfarbe für das Gantt-Chart")
}

# Der magische Data Editor von Streamlit (erlaubt Hinzufügen, Löschen, Bearbeiten)
edited_df = st.data_editor(
    df, 
    column_config=column_config, 
    num_rows="dynamic", 
    use_container_width=True,
    key="grid_editor"
)

# Gespeicherte Daten aktualisieren
st.session_state.project_data = edited_df

# --- HAUPTBEREICH: DAS GANTT-CHART (Die Timeline) ---
st.write("### 📊 Zeitstrahl")

if not edited_df.empty:
    try:
        # Plotly Gantt-Chart erstellen
        fig = px.timeline(
            edited_df, 
            x_start="Start", 
            x_end="Ende", 
            y="Aufgabe", 
            color="Farbe",
            color_discrete_map="identity", # Nutzt die exakten Hex-Farben aus der Tabelle!
            hover_data=["Gruppe", "Status"]
        )
        
        # Design-Anpassungen für den Tom's Planner Vibe
        fig.update_yaxes(autorange="reversed") # Chronologische Reihenfolge von oben nach unten
        fig.update_layout(
            grid=dict(rows=1, columns=1),
            xaxis_title="Zeitverlauf",
            yaxis_title="",
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=400 + (len(edited_df) * 20), # Dynamische Höhe je nach Aufgabenanzahl
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        
        # Gridlines wie im echten Planer hinzufügen
        fig.update_xaxes(
            showgrid=True, 
            gridcolor="#e2e8f0", 
            ticks="outside", 
            tickformat="%d. %b\n%Y",
            dtick="D1" if (max(edited_df['Ende']) - min(edited_df['Start'])).days < 30 else "W1" # Schaltet bei langen Projekten auf Wochenansicht um
        )
        fig.update_yaxes(showgrid=True, gridcolor="#e2e8f0")
        
        # Render Chart
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error("Bitte überprüfe deine Datumsangaben. Das Startdatum muss vor dem Enddatum liegen.")
else:
    st.info("Füge in der Tabelle oben Aufgaben hinzu, um den Zeitstrahl zu generieren.")