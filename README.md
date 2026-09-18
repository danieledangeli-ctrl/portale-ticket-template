# Portale Ticket — template di partenza

Repo di partenza per il laboratorio **API + Frontend** (ITS D.E.Mo.S., XII Ciclo).

Contiene un'API FastAPI che **legge già** dei ticket da un database SQLite:
`GET /health`, `GET /tickets`, `GET /tickets/{id}`. Creare, modificare, cancellare,
filtrare e proteggere le scritture lo costruisci tu, seguendo `CONSEGNA.md`.

## 1. Crea il tuo repository da questo template

1. In alto a destra clicca **Use this template → Create a new repository**.
2. Nel campo *Repository name* GitHub propone un nome casuale (es. `literate-octo-disco`): **cancellalo** e scrivi `portale-ticket`. Visibilità: **Public**.
3. Clicca **Create repository**.

## 2. Apri il Codespace

Il Codespace è il tuo repository già aperto nel cloud: non devi scaricare né clonare nulla sul Mac.

1. Nel **tuo** repository clicca il bottone verde **Code**.
2. Scheda **Codespaces** → **Create codespace on main**.
3. Aspetta 1–2 minuti: si apre VS Code nel browser. In basso a destra compare
   "Running postCreateCommand": sta installando FastAPI. Aspetta che finisca.
4. GitHub dà al Codespace un nome casuale (es. `literate-octo-disco`): non importa. Domani **riapri lo stesso**
   da [github.com/codespaces](https://github.com/codespaces), non crearne uno nuovo.

## 3. Avvia il server

Apri il terminale (menu **Terminal → New Terminal**) e scrivi:

```bash
uvicorn app.main:app --reload
```

Devi vedere una riga tipo:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

## 4. Verifica che funziona

Compare un avviso "La tua applicazione in esecuzione sulla porta 8000 è disponibile":
clicca **Apri nel browser**. Si apre un URL tipo `https://xxx-8000.app.github.dev/`.

Aggiungi in fondo all'URL, uno per volta:

- `/health` → vedi `{"status":"ok"}`.
- `/tickets` → vedi **tre ticket già pronti**. Non li hai scritti tu: il server li inserisce
  al primo avvio, per darti dei dati veri su cui lavorare fin da subito.
- `/docs` → vedi la documentazione interattiva dell'API.

Nell'albero dei file a sinistra è comparso `tickets.db`: è il database, un file solo.
È già nel `.gitignore`, non finirà mai su GitHub.

Se vedi tutte e tre le cose, sei pronto. Apri `CONSEGNA.md` e parti dal passo 0.

## 5. Salva su GitHub — obbligatorio, a ogni passo

Il Codespace può essere cancellato (da GitHub dopo giorni di inattività, o da te per sbaglio). Quello che conta è
il tuo repository su GitHub. **A ogni passo della CONSEGNA completato**, e in ogni caso prima di uscire dall'aula, nel terminale:

```bash
git add .
git commit -m "passo 3: creare i ticket"
git push
```

Verifica: ricarica la pagina del tuo repository su GitHub → vedi i file aggiornati.
**Senza push, domani non hai niente da cui ripartire.**

## Com'è fatto il progetto

| File | Cosa contiene |
|------|---------------|
| `app/main.py` | gli endpoint dell'API: è il file che il browser interroga |
| `app/db.py` | tutto il codice che parla col database. **Nessun altro file contiene SQL** |
| `app/models.py` | che forma deve avere un ticket: FastAPI lo usa per validare i dati |
| `requirements.txt` | le librerie da installare |
| `.env.example` | il modello del file dei segreti. Lo copierai in `.env` al passo 6 |
| `tickets.db` | il database. Compare al primo avvio, non va su GitHub |

## Comandi che userai sempre

| Cosa | Comando |
|------|---------|
| Avviare il server | `uvicorn app.main:app --reload` |
| Fermare il server | `CTRL + C` nel terminale |
| Installare una libreria nuova | `pip install nome-libreria` e poi aggiungila a `requirements.txt` |
| Salvare il lavoro su GitHub (vedi punto 5) | `git add .` → `git commit -m "cosa ho fatto"` → `git push` |
| Ricominciare col database da zero | `rm tickets.db` e riavvia il server: torna ai tre ticket iniziali |

## Se qualcosa non va

- **"command not found: uvicorn"** → l'installazione non è finita o è fallita. Lancia a mano `pip install -r requirements.txt`.
- **"Address already in use"** → c'è già un server acceso. Fermalo con `CTRL + C` nel terminale dove gira, oppure chiudi quel terminale.
- **Vedi una pagina di login di GitHub invece dei dati** → la porta 8000 è impostata su *Private*. Scheda **Ports** in basso,
  tasto destro sulla riga 8000 → **Port Visibility → Public**. Normalmente è già pubblica: la imposta il devcontainer.
- **La pagina resta bianca / errore 502** → il server non è partito. Guarda il terminale: l'errore in rosso dice quale riga di codice è sbagliata.
- **`/tickets` risponde `[]` invece dei tre ticket** → hai cancellato i ticket di esempio. Non è un guasto: `rm tickets.db` e riavvia il server per rifarli comparire.
- **Copilot Chat**: icona a forma di fumetto in alto a destra. Incolla l'errore e chiedi "spiegami questo errore". Spiegare sì, scrivere il codice al posto tuo no: è un esercizio.
