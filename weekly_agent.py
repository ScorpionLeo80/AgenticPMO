import schedule
import time
import subprocess
from datetime import datetime
import logging
import os

# 📁 Crea cartella logs se non esiste
if not os.path.exists("logs"):
    os.makedirs("logs")

# 🕒 Setup log file giornaliero
log_filename = f"logs/weekly_agent_{datetime.now().strftime('%Y%m%d')}.log"

# 🧾 Configura logging
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# ✅ Funzione che esegue lo script principale
def run_agentic_pmo():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"⏰ [AUTO] Esecuzione AgenticPMO – {now}")
    logging.info(f"Esecuzione automatica avviata – {now}")
    try:
        subprocess.run(["python", "agentic_pmo.py"])
        logging.info("Esecuzione completata senza errori.")
    except Exception as e:
        print(f"❌ Errore durante l’esecuzione automatica: {str(e)}")
        logging.error(f"Errore durante esecuzione automatica: {str(e)}")

# ✅ Pianificazione settimanale: ogni venerdì alle 09:00
schedule.every().friday.at("09:00").do(run_agentic_pmo)

print("🧠 Agentic PMO – modalità automatica attivata. In attesa del prossimo venerdì alle 09:00...\n")
logging.info("Weekly agent attivato. In attesa del prossimo venerdì alle 09:00.")

# 🔁 Loop infinito che controlla ogni minuto se è ora di eseguire
while True:
    schedule.run_pending()
    time.sleep(60)
