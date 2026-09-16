# Consegna G1 — Il mio portale ticket, v1

**"L'API che ricorda e che si difende."**

Alla fine hai un'API di gestione ticket che: salva su database, rifiuta i dati sbagliati,
non si fa bucare da una SQL injection e accetta scritture solo con la chiave.

Sei passi. Ogni passo finisce con **"Come verifico"**: non passare al successivo finché la verifica non è verde.
I passi 1–4 li fanno tutti. Il 5 è il traguardo. Se sei in ritardo, il 4 si può saltare senza perdere nulla.

> Regola della giornata: **Copilot autocompletamento spento, Copilot Chat acceso.**
> Alla chat chiedi "spiegami questo errore", non "scrivi il codice".

---

## Passo 0 — Prima di partire

- [ ] Hai creato il tuo repo dal template e aperto il Codespace (vedi `README.md`).
- [ ] Il terminale è aperto in basso (menu **Terminal → New Terminal**).
- [ ] Nell'albero dei file a sinistra vedi `app/main.py`, `requirements.txt`, `.env.example`.
- [ ] Hai letto il punto 5 del `README.md`: **`git add . && git commit -m "..." && git push` alla fine di ogni passo**. Senza push, domani riparti da zero.

---

## Passo 1 — Ambiente pronto: il server risponde

Nel terminale:

```bash
uvicorn app.main:app --reload
```

`--reload` riavvia il server da solo ogni volta che salvi un file. Lascialo acceso per tutto il pomeriggio.
Se devi dare altri comandi, apri un **secondo** terminale (icona `+` nel pannello del terminale).

**Come verifico**

- Compare l'avviso della porta 8000 → **Apri nel browser**.
- Aggiungi `/health` all'URL → vedi `{"status":"ok"}`.
- Aggiungi `/docs` all'URL → vedi la pagina con `GET /health`. Clicca **Try it out → Execute** → risposta `200`.

Se fallisce: guarda il terminale. La riga rossa in fondo dice il file e il numero di riga dell'errore.

---

## Passo 2 — Leggere e creare: `GET /tickets` e `POST /tickets`

Per ora i ticket stanno in una **lista in memoria**: quando il server si riavvia si perdono. Al passo 3 sistemiamo.

### 2a. Il modello dei dati

Crea il file `app/models.py` con:

```python
from typing import Literal
from pydantic import BaseModel, Field

TicketStatus = Literal["aperto", "in_lavorazione", "chiuso"]


class TicketIn(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str = Field(default="", max_length=1000)
    status: TicketStatus = "aperto"


class TicketOut(TicketIn):
    id: int
    created_at: str
```

### 2b. Gli endpoint

Sostituisci **tutto** il contenuto di `app/main.py` con:

```python
from datetime import datetime, timezone
from fastapi import FastAPI

from app.models import TicketIn, TicketOut

app = FastAPI(title="Portale Ticket", version="0.2")

# Provvisorio: i ticket vivono qui finché il server è acceso.
tickets: list[dict] = []
next_id = 1


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tickets", response_model=list[TicketOut])
def list_tickets():
    return tickets


@app.post("/tickets", response_model=TicketOut, status_code=201)
def create_ticket(ticket: TicketIn):
    global next_id
    new_ticket = {
        "id": next_id,
        "title": ticket.title,
        "description": ticket.description,
        "status": ticket.status,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    tickets.append(new_ticket)
    next_id += 1
    return new_ticket
```

Salva. Il terminale dice `Reloading...` e poi `Application startup complete`.

**Come verifico** (tutto da `/docs`, ricarica la pagina)

1. `POST /tickets` → Try it out → nel body scrivi `{"title": "Stampante rotta", "description": "Piano 2"}` → Execute → **201** e il ticket con `id: 1`.
2. `POST /tickets` con `{"title": "ab"}` → **422** e il messaggio `String should have at least 3 characters`.
3. `POST /tickets` con `{"title": "Mouse", "status": "boh"}` → **422**: lo stato non è tra quelli ammessi.
4. `GET /tickets` → **200** e la lista con il ticket creato al punto 1.
5. Nel terminale premi `CTRL+C`, rilancia `uvicorn app.main:app --reload`, rifai `GET /tickets` → lista **vuota**. È il problema che risolviamo ora.

---

## Passo 3 — Ricordare: SQLite, `PUT`, `DELETE`, 404

### 3a. Il modulo database

Crea `app/db.py`. Tutte le query usano i `?`: **nessuna f-string nel SQL, mai.**

```python
import sqlite3
from datetime import datetime, timezone
from typing import Optional

DB_PATH = "tickets.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                status      TEXT NOT NULL DEFAULT 'aperto',
                created_at  TEXT NOT NULL
            )
            """
        )


def list_tickets() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM tickets ORDER BY id").fetchall()
    return [dict(r) for r in rows]


def get_ticket(ticket_id: int) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
    return dict(row) if row else None


def create_ticket(title: str, description: str, status: str) -> dict:
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO tickets (title, description, status, created_at) VALUES (?, ?, ?, ?)",
            (title, description, status, created_at),
        )
        new_id = cursor.lastrowid
    return get_ticket(new_id)


def update_ticket(ticket_id: int, title: str, description: str, status: str) -> Optional[dict]:
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE tickets SET title = ?, description = ?, status = ? WHERE id = ?",
            (title, description, status, ticket_id),
        )
        if cursor.rowcount == 0:
            return None
    return get_ticket(ticket_id)


def delete_ticket(ticket_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
        return cursor.rowcount > 0
```

### 3b. Il server usa il database

Sostituisci **tutto** `app/main.py` con:

```python
from fastapi import FastAPI, HTTPException

from app import db
from app.models import TicketIn, TicketOut

app = FastAPI(title="Portale Ticket", version="0.3")

db.init_db()  # crea la tabella se non c'è


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tickets", response_model=list[TicketOut])
def list_tickets():
    return db.list_tickets()


@app.get("/tickets/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: int):
    ticket = db.get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket non trovato")
    return ticket


@app.post("/tickets", response_model=TicketOut, status_code=201)
def create_ticket(ticket: TicketIn):
    return db.create_ticket(ticket.title, ticket.description, ticket.status)


@app.put("/tickets/{ticket_id}", response_model=TicketOut)
def update_ticket(ticket_id: int, ticket: TicketIn):
    updated = db.update_ticket(ticket_id, ticket.title, ticket.description, ticket.status)
    if updated is None:
        raise HTTPException(status_code=404, detail="Ticket non trovato")
    return updated


@app.delete("/tickets/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: int):
    if not db.delete_ticket(ticket_id):
        raise HTTPException(status_code=404, detail="Ticket non trovato")
```

Nell'albero dei file compare `tickets.db`: è il database. È già nel `.gitignore`, non finirà su GitHub.

**Come verifico** (da `/docs`)

1. `POST /tickets` due volte con titoli diversi → **201**, id `1` e `2`.
2. `GET /tickets/1` → **200**. `GET /tickets/99` → **404** `Ticket non trovato`.
3. `PUT /tickets/1` con `{"title": "Stampante rotta", "status": "chiuso"}` → **200** e lo stato aggiornato.
4. `DELETE /tickets/2` → **204**. Poi `GET /tickets/2` → **404**.
5. **Il test che conta**: `CTRL+C`, rilancia uvicorn, `GET /tickets` → il ticket 1 **c'è ancora**.

---

## Passo 4 — Filtrare: `GET /tickets?status=aperto`

Chi usa il portale vuole vedere solo i ticket aperti. Aggiungiamo un **query parameter**.

### 4a. In `app/db.py` sostituisci `list_tickets` con:

```python
def list_tickets(status: Optional[str] = None) -> list[dict]:
    with get_connection() as conn:
        if status is None:
            rows = conn.execute("SELECT * FROM tickets ORDER BY id").fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM tickets WHERE status = ? ORDER BY id", (status,)
            ).fetchall()
    return [dict(r) for r in rows]
```

### 4b. In `app/main.py`

Aggiungi agli import in alto:

```python
from typing import Optional
from fastapi import Query
from app.models import TicketIn, TicketOut, TicketStatus
```

(la riga `from app.models import ...` sostituisce quella che c'era). Poi sostituisci l'endpoint `GET /tickets` con:

```python
@app.get("/tickets", response_model=list[TicketOut])
def list_tickets(status: Optional[TicketStatus] = Query(default=None)):
    return db.list_tickets(status)
```

**Come verifico**

1. Crea un ticket con `status: "chiuso"` e uno con `status: "aperto"`.
2. Nel browser: `.../tickets?status=aperto` → solo gli aperti. `.../tickets?status=chiuso` → solo i chiusi. `.../tickets` → tutti.
3. `.../tickets?status=boh` → **422**: `TicketStatus` ammette solo tre valori.
4. `.../tickets?status=' OR '1'='1` → **422**. Anche se passasse la validazione, il `?` nella query lo tratterebbe come testo. Due difese.

---

## Passo 5 — Difendersi: la chiave `X-API-Key`

Leggere è libero. Scrivere solo con la chiave. La chiave **non sta nel codice**: sta in una variabile d'ambiente.

### 5a. Il file `.env`

Nel terminale (il secondo, non quello di uvicorn):

```bash
cp .env.example .env
```

Apri `.env` e cambia il valore: `API_KEY=una-frase-lunga-che-sai-solo-tu`. Salva.
`.env` è nel `.gitignore`: **non** verrà mai committato. `.env.example` sì, ma è vuoto di segreti.

### 5b. In `app/main.py`

Import in alto (aggiungi):

```python
import os
from dotenv import load_dotenv
from fastapi import Depends, Header
```

Subito dopo gli import, **prima** di `app = FastAPI(...)`:

```python
load_dotenv()
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("Manca API_KEY: copia .env.example in .env e imposta una chiave.")
```

Dopo `db.init_db()`, la **guardia**:

```python
def require_api_key(x_api_key: Optional[str] = Header(default=None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Chiave API mancante o errata")
```

Infine aggiungi `dependencies=[Depends(require_api_key)]` ai **tre** decoratori delle scritture:

```python
@app.post("/tickets", response_model=TicketOut, status_code=201, dependencies=[Depends(require_api_key)])
...
@app.put("/tickets/{ticket_id}", response_model=TicketOut, dependencies=[Depends(require_api_key)])
...
@app.delete("/tickets/{ticket_id}", status_code=204, dependencies=[Depends(require_api_key)])
```

I `GET` restano liberi.

**Come verifico** (da `/docs`, ricarica: nei tre endpoint protetti è comparso il campo `x-api-key`)

1. `POST /tickets` **senza** compilare `x-api-key` → **401** `Chiave API mancante o errata`.
2. `POST /tickets` con `x-api-key` = la chiave del tuo `.env` → **201**.
3. `GET /tickets` senza chiave → **200**: leggere è libero.
4. `DELETE /tickets/1` con chiave sbagliata → **401**. Con quella giusta → **204**.
5. Nel terminale: `git status` → `.env` **non** compare tra i file da committare. `tickets.db` nemmeno.

---

## Passo 6 — Test finale: l'API ricorda e si difende

Spunta tutto. Se una riga non è verde, torna al passo indicato.

| Test | Come | Atteso | Passo |
|------|------|--------|-------|
| Ricorda | riavvia uvicorn, `GET /tickets` | i ticket ci sono ancora | 3 |
| Rifiuta dati sbagliati | `POST` con `{"title": "ab"}` (con chiave) | **422** | 2 |
| Rifiuta stati inventati | `POST` con `"status": "boh"` | **422** | 2 |
| Non esiste → 404 | `GET /tickets/9999` | **404** | 3 |
| Filtra | `?status=aperto` | solo gli aperti | 4 |
| Injection nel filtro | `?status=' OR '1'='1` | **422**, nessun dato extra | 4 |
| Injection nel body | `POST` con `{"title": "x'); DROP TABLE tickets; --"}` (con chiave) | **201**, salvato come testo, poi `GET /tickets` funziona ancora | 3 |
| Senza chiave | `POST` senza `x-api-key` | **401** | 5 |
| Chiave sbagliata | `DELETE /tickets/1` con chiave `abc` | **401** | 5 |
| Segreti fuori dal repo | `git status` | `.env` e `tickets.db` non compaiono | 5 |

Poi salva il lavoro:

```bash
git add .
git commit -m "Portale ticket v1: CRUD, SQLite, validazione, API key"
git push
```

**Come verifico:** su GitHub, nel tuo repo, vedi `app/db.py` e `app/models.py`. **Non** vedi `.env` né `tickets.db`.

Domani questa API va online e ci mettiamo davanti una pagina web.

---

## Se ti perdi

- Chiedi. La soluzione completa ce l'ha il docente: serve per **confrontare**, non per copiare, perché domani riparti dal tuo codice.
- Gli errori tipici li raccogliamo insieme negli ultimi 30 minuti: diventano domande della verifica.
