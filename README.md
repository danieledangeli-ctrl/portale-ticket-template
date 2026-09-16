# Portale Ticket — template di partenza

Repo di partenza per il laboratorio **API + Frontend** (ITS D.E.Mo.S., XII Ciclo).
Contiene un server FastAPI con un solo endpoint (`GET /health`). Il resto lo costruisci tu.

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

- Aggiungi `/health` alla fine dell'URL → vedi `{"status":"ok"}`.
- Aggiungi `/docs` alla fine dell'URL → vedi la documentazione interattiva dell'API.

Se vedi entrambe le cose, sei pronto. Apri `CONSEGNA.md` e parti dal passo 1.

## 5. Salva su GitHub — obbligatorio, a ogni passo

Il Codespace può essere cancellato (da GitHub dopo giorni di inattività, o da te per sbaglio). Quello che conta è
il tuo repository su GitHub. **A ogni passo della CONSEGNA completato**, e in ogni caso prima di uscire dall'aula, nel terminale:

```bash
git add .
git commit -m "passo 3: SQLite"
git push
```

Verifica: ricarica la pagina del tuo repository su GitHub → vedi i file aggiornati.
**Senza push, domani non hai niente da cui ripartire.**

## Comandi che userai sempre

| Cosa | Comando |
|------|---------|
| Avviare il server | `uvicorn app.main:app --reload` |
| Fermare il server | `CTRL + C` nel terminale |
| Installare una libreria nuova | `pip install nome-libreria` e poi aggiungila a `requirements.txt` |
| Salvare il lavoro su GitHub (vedi punto 5) | `git add .` → `git commit -m "cosa ho fatto"` → `git push` |

## Se qualcosa non va

- **"command not found: uvicorn"** → l'installazione non è finita o è fallita. Lancia a mano `pip install -r requirements.txt`.
- **"Address already in use"** → c'è già un server acceso. Fermalo con `CTRL + C` nel terminale dove gira, oppure chiudi quel terminale.
- **La pagina resta bianca / errore 502** → il server non è partito. Guarda il terminale: l'errore in rosso dice quale riga di codice è sbagliata.
- **Copilot Chat**: icona a forma di fumetto in alto a destra. Incolla l'errore e chiedi "spiegami questo errore". Spiegare sì, scrivere il codice al posto tuo no: è un esercizio.
