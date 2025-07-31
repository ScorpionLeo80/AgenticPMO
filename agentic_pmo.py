import subprocess
import os
from datetime import datetime

# Prompt completo che vogliamo inviare a phi3
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

# Comando per avviare il modello Ollama locale
cmd = ["ollama", "run", "phi3"]

try:
    print("🧠 Invio prompt a phi3...")

    # Esecuzione del comando Ollama con input del prompt
    result = subprocess.run(
        cmd,
        input=PROMPT.encode('utf-8'),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Decodifica dell'output ricevuto
    output = result.stdout.decode('utf-8')
    print("✅ Risposta generata da phi3:\n")
    print(output)

    # 🔁 Creiamo un timestamp per salvare i file con nome univoco
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ✅ Salviamo l'intero output in Markdown
    markdown_file = f"output/piano_progetto_{timestamp}.md"
    with open(markdown_file, "w", encoding="utf-8") as f:
        f.write(output)
    print(f"📄 Piano salvato in formato Markdown: {markdown_file}")

    # 🔍 Estrazione dei task dalla sezione 🧩
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

    # ✅ Salviamo i task in formato CSV
    csv_file = f"output/piano_task_{timestamp}.csv"
    with open(csv_file, "w", encoding="utf-8") as f:
        f.write("Task,Descrizione\n")
        for task, desc in tasks:
            desc = desc.replace(",", ";")  # per evitare errori nei CSV
            f.write(f"{task.strip()},{desc.strip()}\n")

    print(f"📊 Task salvati in formato CSV: {csv_file}")

except Exception as e:
    print("❌ Errore durante l'esecuzione:", str(e))
