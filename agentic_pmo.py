import subprocess
import os
from datetime import datetime
import logging

# 📁 Prepara directory dei log
if not os.path.exists("logs"):
    os.makedirs("logs")

# 🕒 Timestamp per versionare file di log
log_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f"logs/agentic_run_{log_timestamp}.log"

# 🧾 Configura logging parlante
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Prompt completo da inviare al modello
PROMPT = """
Sei un assistente project manager intelligente. Riceverai un obiettivo di progetto e dovrai generare un piano esecutivo.

Per favore segui questa struttura nell’output:

🎯 Obiettivo:
(sintesi dell’obiettivo)

📅 Milestone (con scadenze relative o assolute):
- (Nome milestone) – (Data o settimana stimata)
- …

🧩 Task principali (con descrizione sintetica):
- Task 1: ...
- Task 2: ...
- …

⏳ Timeline suggerita:
(Settimane o mesi, timeline logica coerente)

🔁 Considera un team di 4 persone e una durata di 3 mesi. Pianifica con realismo e buon senso.

Obiettivo del progetto: Migrazione di un'applicazione web su AWS.
"""

cmd = ["ollama", "run", "phi3"]

try:
    print("🧠 Invio prompt a phi3...")
    logging.info("Prompt inviato al modello phi3")

    result = subprocess.run(
        cmd,
        input=PROMPT.encode('utf-8'),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    output = result.stdout.decode('utf-8')
    error_output = result.stderr.decode('utf-8')

    if output.strip():
        print("✅ Risposta generata da phi3:\n")
        print(output)
        logging.info("Risposta ricevuta dal modello")
        logging.info(output)
    else:
        print("⚠️ Nessuna risposta ricevuta dal modello")
        logging.warning("Nessuna risposta generata da phi3")

    # ⏳ Timestamp per nomi dei file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 📄 Salvataggio del piano completo in Markdown
    markdown_file = f"output/piano_progetto_{timestamp}.md"
    with open(markdown_file, "w", encoding="utf-8") as f:
        f.write(output)
    print(f"📄 Piano salvato in formato Markdown: {markdown_file}")
    logging.info(f"Piano salvato in Markdown: {markdown_file}")

    # 📊 Estrazione dei task
    tasks = []
    inside_task_section = False
    for line in output.splitlines():
        if "🧩" in line:
            inside_task_section = True
            continue
        if inside_task_section:
            if line.strip() == "" or line.startswith("⏳") or line.startswith("🔁"):
                break
            if "Task" in line or "task" in line:
                parts = line.split(" - ", 1)
                if len(parts) == 2:
                    tasks.append(parts)

    if tasks:
        csv_file = f"output/piano_task_{timestamp}.csv"
        with open(csv_file, "w", encoding="utf-8") as f:
            f.write("Task,Descrizione\n")
            for task, desc in tasks:
                desc = desc.replace(",", ";")
                f.write(f"{task.strip()},{desc.strip()}\n")
        print(f"📊 Task salvati in formato CSV: {csv_file}")
        logging.info(f"Task salvati in CSV: {csv_file}")
    else:
        print("⚠️ Nessun task trovato nel testo generato")
        logging.warning("Nessun task rilevato nella sezione 🧩")

except Exception as e:
    print("❌ Errore durante l'esecuzione:", str(e))
    logging.error(f"Errore durante esecuzione: {str(e)}")
