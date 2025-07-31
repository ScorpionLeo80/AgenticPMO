import subprocess
import os
from datetime import datetime
import logging
import sys

# 📁 Legge il workspace dalla riga di comando, default = output/
workspace = sys.argv[1] if len(sys.argv) > 1 else "output/"
os.makedirs(workspace, exist_ok=True)

# 🕒 Timestamp per versione file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# 🧾 Log in cartella progetto
log_file = os.path.join(workspace, f"agentic_run_{timestamp}.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# 📥 Lettura del prompt dal file
prompt_path = os.path.join(workspace, "prompt.txt")
if not os.path.exists(prompt_path):
    print("❌ prompt.txt non trovato nel workspace.")
    logging.error("File prompt.txt mancante nel workspace.")
    sys.exit(1)

with open(prompt_path, "r", encoding="utf-8") as f:
    PROMPT = f.read()

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

    # 📄 Salvataggio piano in Markdown
    markdown_file = os.path.join(workspace, f"piano_progetto_{timestamp}.md")
    with open(markdown_file, "w", encoding="utf-8") as f:
        f.write(output)
    print(f"📄 Piano salvato in formato Markdown: {markdown_file}")
    logging.info(f"Piano salvato in Markdown: {markdown_file}")

    # 📊 Estrazione dei task con parser flessibile
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
                # Accetta sia "-" che ":" come separatori
                if " - " in line:
                    parts = line.split(" - ", 1)
                elif ":" in line:
                    parts = line.split(":", 1)
                else:
                    continue
                if len(parts) == 2:
                    tasks.append(parts)

    if tasks:
        csv_file = os.path.join(workspace, f"piano_task_{timestamp}.csv")
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
