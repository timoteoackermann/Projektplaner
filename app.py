import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Seiteneinstellung für Breitbild
st.set_page_config(layout="wide", page_title="Tom's Planner Clone", page_icon="📊")

# CSS für das originale Tom's Planner Design (Orange Akzente & Clean Grid)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h3 { color: #1e293b; font-family: 'Helvetica Neue', Arial, sans-serif; }
    /* Schickere Tabellen-Überschrift */
    .table-header {
        background-color: #ff6b00;
        color: white;
        padding: 10px;
        border-radius: 4px 4px 0 0;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Mein Projektplaner")
st.markdown("### Exakter Nachbau nach deiner Vorlage (inkl. Abhängigkeiten & Meilensteinen)")

# --- INITIALE DATEN (Eins zu eins aus deinem Screenshot) ---
if 'project_data' not in st.session_state:
    default_data = [
        # DESIGN PHASE (Blau)
        {"Gruppe": "1. Design", "Aufgabe": "Building design", "Ressource": "Architekt", "Status": "In Arbeit", "Start": "2026-06-24", "Ende": "2026-09-02", "Typ": "Aufgabe", "Farbe": "#0284c7", "Abhängig von": ""},
        {"Gruppe": "1. Design", "Aufgabe": "Interior layout", "Ressource": "Designer", "Status": "Geplant", "Start": "2026-08-01", "Ende": "2026-09-02", "Typ": "Aufgabe", "Farbe": "#0284c7", "Abhängig von": ""},
        {"Gruppe": "1. Design", "Aufgabe": "Design completed", "Ressource": "Alle", "Status": "Geplant", "Start": "2026-09-02", "Ende": "2026-09-02", "Typ": "Meilenstein", "Farbe": "#ef4444", "Abhängig von": "Building design"},
        
        # SITE SELECTION (Grün)
        {"Gruppe": "2. Site selection", "Aufgabe": "Create list of 3 possible...", "Ressource": "Management", "Status": "Fertig", "Start": "2026-06-24", "Ende": "2026-07-08", "Typ": "Aufgabe", "Farbe": "#22c55e", "Abhängig von": ""},
        {"Gruppe": "2. Site selection", "Aufgabe": "Soil evaluation", "Ressource": "Gutachter", "Status": "Fertig", "Start": "2026-08-12", "Ende": "2026-09-02", "Typ": "Aufgabe", "Farbe": "#22c55e", "Abhängig von": ""},
        
        # CONSTRUCTION (Braun)
        {"Gruppe": "3. Construction", "Aufgabe": "Foundation", "Ressource": "Rohbau-Team", "Status": "Geplant", "Start": "2026-09-09", "Ende": "2026-10-14", "Typ": "Aufgabe", "Farbe": "#b45309", "Abhängig von": "Design completed"},
        {"Gruppe": "3. Construction", "Aufgabe": "Framing", "Ressource": "Zimmermann", "Status": "Geplant", "Start": "2026-10-14", "Ende": "2026-11-18", "Typ": "Aufgabe", "Farbe": "#b45309", "Abhängig von": "Foundation"},
        {"Gruppe": "3. Construction", "Aufgabe": "Walls", "Ressource": "Maurer", "Status": "Geplant", "Start": "2026-11-18", "Ende": "2026-12-23", "Typ": "Aufgabe", "Farbe": "#b45309", "Abhängig von": "Framing"},
        {"Gruppe": "3. Construction", "Aufgabe": "Roof", "Ressource": "Dachdecker", "Status": "Geplant", "Start": "2026-12-23", "Ende": "2027-01-27", "Typ": "Aufgabe", "Farbe": "#b45309", "Abhängig von": "Walls"},
        
        # INTERIOR DESIGN (Lila)
        {"Gruppe": "4. Interior design", "Aufgabe": "Electrical wiring", "Ressource": "Elektro", "Status": "Geplant", "Start": "2027-01-27", "Ende": "2027-02-15", "Typ": "Aufgabe", "Farbe": "#a855f7", "Abhängig von": "Roof"},
        {"Gruppe": "4. Interior design", "Aufgabe": "Plumbing", "Ressource": "Sanitär", "Status": "Geplant", "Start": "2027-02-15", "Ende": "2027-03-05", "Typ": "Aufgabe", "Farbe": "#a855f7", "Abhängig von": "Electrical wiring"},
    ]
    st.session_state.project_data = pd.DataFrame(default_data)

df = st.session_state.project_data

# Daten-Typen konvertieren
df['Start'] = pd.to_datetime(df['Start']).dt.date
df['Ende'] = pd.to_datetime(df['Ende']).dt.date

# --- SIDEBAR ---
st.sidebar.header("⚙️ Steuerung")
st.sidebar.markdown("""
**Bedienung wie im Original:**
* **Neue Zeile:** Klicke unten in der Tabelle auf das `+`.
* **Abhängigkeit:** Trage bei *'Abhängig von'* exakt den Namen der Vorgänger-Aufgabe ein.
* **Meilenstein:** Schalte den Typ auf 'Meilenstein' um, um die rote Flagge zu erzeugen.
""")

csv = df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("📥 Excel/CSV Export", data=csv, file_name="projektplan.csv", mime="text/csv")

if st.sidebar.button("🔄 Plan zurücksetzen"):
    st.session_state.clear()
    st.rerun()

# --- LINKER BEREICH: DIE TABELLE ---
st.markdown('<div class="table-header">📋 Aufgaben & Ressourcen (Tom\'s Grid Look)</div>', unsafe_allow_html=True)

column_config = {
    "Gruppe": st.column_config.SelectboxColumn("Phase / Ordner", options=["1. Design", "2. Site selection", "3. Construction", "4. Interior design"], required=True),
    "Aufgabe": st.column_config.TextColumn("Activity (Aufgabe)", required=True),
    "Ressource": st.column_config.TextColumn("Resource"),
    "Status": st.column_config.SelectboxColumn("Status", options=["Geplant", "In Arbeit", "Fertig"]),
    "Start": st.column_config.DateColumn("Start", format="YYYY-MM-DD"),
    "Ende": st.column_config.DateColumn("Ende", format="YYYY-MM-DD"),
    "Typ": st.column_config.SelectboxColumn("Typ", options=["Aufgabe", "Meilenstein"]),
    "Abhängig von": st.column_config.TextColumn("Abhängig von (Exakter Name)"),
    "Farbe": st.column_config.SelectboxColumn("Farbe", options=["#0284c7", "#22c55e", "#b45309", "#a855f7", "#ef4444"])
}

edited_df = st.data_editor(
    df,
    column_config=column_config,
    num_rows="dynamic",
    use_container_width=True,
    key="toms_editor"
)
st.session_state.project_data = edited_df

# --- RECHTER BEREICH: DAS GANTT-CHART MIT ABHÄNGIGKEITEN ---
st.write("### 📊 Zeitstrahl & Timeline-Verknüpfungen")

if not edited_df.empty:
    # Sortieren nach Gruppe und Datum, damit die Reihenfolge von oben nach unten stimmt
    edited_df = edited_df.sort_values(by=["Gruppe", "Start"], ascending=[True, False])
    
    fig = go.Figure()
    
    # 1. Tasks & Meilensteine zeichnen
    for idx, row in edited_df.iterrows():
        if row['Typ'] == "Meilenstein":
            # Rote Flagge / Raute für Meilensteine wie im Bild
            fig.add_trace(go.Scatter(
                x=[row['Start']],
                y=[row['Aufgabe']],
                mode="markers+text",
                marker=dict(symbol="diamond", size=14, color="#ef4444", line=dict(color="#b91c1c", width=2)),
                name="Meilenstein",
                hoverinfo="text",
                hovertext=f"<b>{row['Aufgabe']}</b><br>Datum: {row['Start']}"
            ))
        else:
            # Normale Balken für Aufgaben
            fig.add_trace(go.Bar(
                x=[(row['Ende'] - row['Start']).days],
                y=[row['Aufgabe']],
                base=[row['Start']],
                orientation='h',
                marker=dict(color=row['Farbe'], line=dict(color="#1e293b", width=0.5)),
                hoverinfo="text",
                hovertext=f"<b>{row['Aufgabe']}</b><br>Ressource: {row['Ressource']}<br>Dauer: {row['Start']} bis {row['Ende']}"
            ))

    # 2. ABHÄNGIGKEITSLINIEN (Die Verbindungs-Pfeile)
    for idx, row in edited_df.iterrows():
        vorganger_name = row['Abhängig von']
        if pd.notna(vorganger_name) and vorganger_name.strip() != "":
            # Suche die Vorgänger-Aufgabe in der Tabelle
            vorganger = edited_df[edited_df['Aufgabe'] == vorganger_name.strip()]
            
            if not vorganger.empty:
                vorganger_ende = vorganger.iloc[0]['Ende']
                nachfolger_start = row['Start']
                
                # Pfeil zeichnen vom Ende des Vorgängers zum Start des Nachfolgers
                fig.add_annotation(
                    x=nachfolger_start,
                    y=row['Aufgabe'],
                    ax=vorganger_ende,
                    ay=vorganger.iloc[0]['Aufgabe'],
                    xref="x", yref="y",
                    axref="x", ayref="y",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor="#64748b", # Edles Slate-Grau für die Verbindungslinien
                )

    # Layout-Design exakt an die Vorlage anpassen (Hintergrund, Raster, Zeitleiste)
    fig.update_layout(
        plot_bgcolor="#f8fafc",
        paper_bgcolor="white",
        showlegend=False,
        height=350 + (len(edited_df) * 28), # Dynamische Höhe für optimale Lesbarkeit
        margin=dict(l=20, r=20, t=40, b=20),
        barmode='stack',
        xaxis=dict(
            type='date',
            showgrid=True,
            gridcolor="#e2e8f0",
            title="Zeitverlauf",
            side="top", # Zeitleiste oben wie im Originalbild
            tickformat="%b %Y",
            dtick="M1" # Monatliche Unterteilung
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#e2e8f0",
            title=""
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Füge Aufgaben in die Tabelle ein, um den Zeitstrahl zu laden.")