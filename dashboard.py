import streamlit as st
import subprocess
import os
import glob
import logging
import pandas as pd
import json
import plotly.express as px
from datetime import datetime

# --- CONFIGURAZIONE PMO E PROGETTO ---
PMO_LIST = ["Renato", "Laura"]
st.sidebar.title("👥 Project Manager")
pmos = st.sidebar.selectbox("Seleziona PMO", PMO_LIST)

st.sidebar.title("📁 Progetto")
existing_projects = os.listdir(f"data/{pmos}") if os.path.exists(f"data/{pmos}") else []
proj_sel = st.sidebar.selectbox("Progetto esistente", existing_projects)
proj_new = st.sidebar.text_input("Oppure inserisci nuovo progetto")

progetto = proj_new.strip() if proj_new.strip() else proj_sel
if not progetto:
    st.warning("🔺 Inserisci o seleziona un progetto per continuare.")
    st.stop()

workspace = os.path.join("data", pmos, progetto)
os.makedirs(workspace, exist_ok=True)

# --- LOGGING ---
log_filename = os.path.join(workspace, f"dashboard_{datetime.now().strftime('%Y%m%d')}.log")
if not os.path.exists("logs"):
    os.makedirs("logs")
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logging.info(f"Dashboard avviata: PMO={pmos}, Progetto={progetto}")

st.title(f"📡 Agentic PMO – {pmos} / {progetto}")

# === PROMPT GUIDATO ===
st.subheader("🧠 Raccolta dati progetto – Prompt guidato")

prompt_data_file = os.path.join(workspace, "prompt_dati.json")
if os.path.exists(prompt_data_file):
    with open(prompt_data_file, "r", encoding="utf-8") as f:
        saved_data = json.load(f)
else:
    saved_data = {}

with st.form("prompt_form"):
    obiettivo = st.text_area("🎯 Obiettivo del progetto", value=saved_data.get("obiettivo", ""))
    durata = st.text_input("⏳ Durata stimata", value=saved_data.get("durata", ""))
    team = st.text_input("👥 Team coinvolto", value=saved_data.get("team", ""))
    milestone = st.text_area("📅 Milestone previste", value=saved_data.get("milestone", ""))
    task_previsti = st.text_area("🧩 Task principali", value=saved_data.get("task", ""))
    criticità = st.text_area("⚠️ Rischi e vincoli", value=saved_data.get("criticità", ""))
    submitted = st.form_submit_button("💾 Salva e genera prompt")

if submitted:
    data = {
        "obiettivo": obiettivo,
        "durata": durata,
        "team": team,
        "milestone": milestone,
        "task": task_previsti,
        "criticità": criticità
    }
    with open(prompt_data_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    prompt_generato = f"""
Sei un assistente project manager intelligente. Crea un piano esecutivo per il seguente progetto.

🎯 Obiettivo:
{obiettivo}

⏳ Durata stimata:
{durata}

👥 Team coinvolto:
{team}

📅 Milestone:
{milestone}

🧩 Task principali:
{task_previsti}

⚠️ Rischi e criticità:
{criticità}

🔁 Genera un piano realistico, dettagliato e strutturato per questo scenario.
"""
    with open(os.path.join(workspace, "prompt.txt"), "w", encoding="utf-8") as f:
        f.write(prompt_generato)
    st.success("✅ Prompt salvato in prompt.txt")

# === GENERAZIONE CON MODELLO ===
if st.button("📌 Genera nuovo piano di progetto"):
    logging.info("▶️ Cliccato 'Genera nuovo piano'")
    subprocess.run(["python", "agentic_pmo.py", workspace])
    st.success("✅ Piano generato")
    logging.info("✅ agentic_pmo.py completato")

# === VISUALIZZAZIONE PIANO ===
markdown_files = sorted(glob.glob(os.path.join(workspace, "*.md")), reverse=True)
csv_files = sorted(glob.glob(os.path.join(workspace, "*.csv")), reverse=True)

st.subheader("📄 Ultimo piano (Markdown)")
if markdown_files:
    with open(markdown_files[0], "r", encoding="utf-8") as f:
        st.markdown(f.read())
    logging.info(f"📄 Piano Markdown caricato: {markdown_files[0]}")
else:
    st.info("Nessun piano Markdown trovato")

# === VISUALIZZAZIONE TASK CSV ===
st.subheader("📊 Ultimi task (CSV)")
if csv_files:
    df = pd.read_csv(csv_files[0])
    st.dataframe(df)
    logging.info(f"📊 CSV caricato: {csv_files[0]}")
else:
    st.info("Nessun CSV trovato")

# === TIMELINE VISIVA ===
st.subheader("📅 Timeline dei task – stato attuale")
if csv_files and {"Task", "Descrizione", "Scadenza", "Stato"}.issubset(df.columns):
    df["Scadenza"] = pd.to_datetime(df["Scadenza"], errors="coerce")
    oggi = pd.Timestamp.now()

    def get_status(row):
        if str(row["Stato"]).strip().lower() == "done":
            return "✅ Completato"
        elif row["Scadenza"] < oggi:
            return "❌ In ritardo"
        else:
            return "🕒 Da fare"

    df["StatoVisuale"] = df.apply(get_status, axis=1)

    fig = px.timeline(
        df,
        x_start="Scadenza",
        x_end="Scadenza",
        y="Task",
        color="StatoVisuale",
        hover_data=["Descrizione", "Scadenza", "Stato"]
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        title="📅 Timeline Task – Stato Attuale",
        xaxis_title="Scadenza",
        yaxis_title="Task",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

# === MODIFICA E RIPIANIFICAZIONE TASK ===
st.subheader("📝 Modifica e ripianifica i task")
if csv_files and {"Task", "Descrizione", "Scadenza", "Stato"}.issubset(df.columns):
    df["Scadenza"] = pd.to_datetime(df["Scadenza"], errors="coerce").dt.date
    df_edit = st.data_editor(df[["Task", "Descrizione", "Scadenza", "Stato"]], num_rows="dynamic", use_container_width=True)

    if st.button("💾 Salva modifiche e aggiorna pianificazione"):
        oggi = datetime.now().date()
        df_edit["Nuova Scadenza"] = df_edit.apply(
            lambda row: row["Scadenza"] if row["Stato"].lower() == "done" or row["Scadenza"] >= oggi
            else oggi + pd.Timedelta(days=3),
            axis=1
        )
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        updated_csv = os.path.join(workspace, f"piano_task_modificato_{timestamp}.csv")
        df_edit.to_csv(updated_csv, index=False)
        st.success(f"✅ Task aggiornati salvati in:\n`{updated_csv}`")
        logging.info(f"✅ Task modificati e salvati in {updated_csv}")
