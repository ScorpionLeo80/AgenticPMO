# 🧠 AgenticPMO – Pianificatore Progetti Locale con Ollama + LLM

Questo progetto implementa un **Agente Intelligente Agentico** in Python che:
- Riceve un obiettivo di progetto (es. migrazione su AWS)
- Genera milestone, task, e timeline
- Salva il piano in `.md` (leggibile) e `.csv` (strutturato)

✅ 100% locale  
✅ Funziona con [Ollama](https://ollama.com) e modelli leggeri come `phi3`  
✅ Nessun costo o API esterna

---

## 🚀 Come funziona

1. L'utente inserisce un obiettivo nel prompt (es. "migrare app su AWS in 3 mesi con 4 persone")
2. LLM locale (`phi3` via Ollama) genera:
   - 🎯 Obiettivo sintetico
   - 📅 Milestone
   - 🧩 Task dettagliati
   - ⏳ Timeline
3. I risultati vengono salvati in `output/`:
   - `piano_progetto_YYYYMMDD_HHMMSS.md`
   - `piano_task_YYYYMMDD_HHMMSS.csv`

---

## 🛠 Requisiti

- Python 3.10+
- [Ollama](https://ollama.com) installato
- Modello `phi3` scaricato (eseguibile con `ollama run phi3`)

---

## ▶️ Esecuzione

```bash
python agentic_pmo.py
