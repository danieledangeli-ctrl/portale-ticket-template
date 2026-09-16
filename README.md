# Portale Ticket — template di partenza

Repo di partenza per il laboratorio **API + Frontend** (ITS D.E.Mo.S., XII Ciclo).
Contiene un server FastAPI con un solo endpoint (`GET /health`). Il resto lo costruisci tu.

## 1. Crea il tuo repository da questo template

1. In alto a destra clicca **Use this template → Create a new repository**.
2. Nome: `portale-ticket` (o come preferisci). Visibilità: **Public**.
3. Clicca **Create repository**.

## 2. Apri il Codespace

1. Nel **tuo** repository clicca il bottone verde **Code**.
2. Scheda **Codespaces** → **Create codespace on main**.
3. Aspetta 1–2 minuti: si apre VS Code nel browser. In basso a destra compare
   "Running postCreateCommand": sta installando FastAPI. Aspetta che finisca.

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

## Comandi che userai sempre

| Cosa | Comando |
|------|---------|
| Avviare il server | `uvicorn app.main:app --reload` |
| Fermare il server | `CTRL + C` nel terminale |
| Installare una libreria nuova | `pip install nome-libreria` e poi aggiungila a `requirements.txt` |
| Salvare il lavoro su GitHub | `git add .` → `git commit -m "cosa ho fatto"` → `git push` |

## Se qualcosa non va

- **"command not found: uvicorn"** → l'installazione non è finita o è fallita. Lancia a mano `pip install -r requirements.txt`.
- **"Address already in use"** → c'è già un server acceso. Fermalo con `CTRL + C` nel terminale dove gira, oppure chiudi quel terminale.
- **La pagina resta bianca / errore 502** → il server non è partito. Guarda il terminale: l'errore in rosso dice quale riga di codice è sbagliata.
- **Copilot Chat**: icona a forma di fumetto in alto a destra. Incolla l'errore e chiedi "spiegami questo errore". Spiegare sì, scrivere il codice al posto tuo no: è un esercizio.
