# Consegna G1 — Il mio portale ticket, v1

**"L'API che ricorda e che si difende."**

Parti da un'API che **legge già** dei ticket da un database. Alla fine della giornata quell'API
sa anche creare, modificare e cancellare, rifiuta i dati sbagliati, non si fa bucare da una
SQL injection e accetta scritture solo con la chiave.

Sette passi. Ognuno finisce con **"Come verifico"**: non passare al successivo finché la verifica non è verde.
I passi 1–4 li fanno tutti. Il 6 è il traguardo. Se sei in ritardo, il 5 si può saltare senza perdere nulla.

> Regola della giornata: **Copilot autocompletamento spento, Copilot Chat acceso.**
> Alla chat chiedi "spiegami questo errore", non "scrivi il codice".

---

## Passo 0 — Prima di partire

- [ ] Hai creato il tuo repo dal template e aperto il Codespace (vedi `README.md`).
- [ ] Il terminale è aperto in basso (menu **Terminal → New Terminal**).
- [ ] Nell'albero dei file a sinistra vedi `app/main.py`, `app/db.py`, `app/models.py`, `requirements.txt`, `.env.example`.
- [ ] Hai letto il punto 5 del `README.md`: **`git add . && git commit -m "..." && git push` alla fine di ogni passo**. Senza push, domani riparti da zero.

---

## Passo 1 — Ambiente pronto: il server risponde e mostra dei dati

Nel terminale:

```bash
uvicorn app.main:app --reload
```

`--reload` riavvia il server da solo ogni volta che salvi un file. Lascialo acceso per tutto il pomeriggio.
Se devi dare altri comandi, apri un **secondo** terminale (icona `+` nel pannello del terminale).

**Come verifico**

- Compare l'avviso della porta 8000 → **Apri nel browser**.
- Aggiungi `/health` all'URL → vedi `{"status":"ok"}`.
- Aggiungi `/tickets` all'URL → vedi **tre ticket già pronti**. Non li hai scritti tu: li ha inseriti
  il server al primo avvio, per darti qualcosa su cui lavorare.
- Aggiungi `/docs` all'URL → vedi la pagina con i tre endpoint che esistono adesso:
  `GET /health`, `GET /tickets`, `GET /tickets/{ticket_id}`.
  Clicca **Try it out → Execute** su `GET /tickets` → risposta `200`.

Nell'albero dei file è comparso `tickets.db`: è il database, un file solo.
È già nel `.gitignore`, non finirà su GitHub.

Se fallisce: guarda il terminale. La riga rossa in fondo dice il file e il numero di riga dell'errore.

---

## Passo 2 — Capire quello che c'è

In questo passo **non scrivi codice**. Apri i tre file e guardali con il docente: quello che
c'è dentro è esattamente quello che aggiungerai tu nei passi successivi.

### `app/models.py` — che forma ha un ticket

`TicketIn` sono i dati che arrivano da fuori, `TicketOut` quelli che rispondiamo.
Nota due cose:

- `TicketIn` **non ha l'id né created_at**: li decide il server. Se li decidesse il client,
  chiunque potrebbe scrivere sopra il ticket di un altro.
- `TicketStatus` ammette **solo tre parole**. Qualunque altra cosa verrà rifiutata, e non
  perché l'abbiamo controllata noi a mano: lo fa FastAPI leggendo il modello.

### `app/db.py` — tutto il SQL sta qui

Nessun'altra parte del programma tocca il database. In `main.py` vogliamo leggere gli
endpoint senza vedere il SQL di mezzo.

Guarda com'è scritta ogni query:

```python
conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
```

Il valore non è dentro la stringa: sta fuori, e al suo posto c'è un `?`.
**Questa è la difesa contro la SQL injection**, e vale per ogni query che scriverai oggi.
Al passo 7 proviamo cosa succede a chi non lo fa.

Guarda anche `seed_if_empty()`: prima conta le righe, e se ce n'è anche una sola non fa niente.
Senza quel controllo, ogni volta che salvi un file `--reload` riavvia il server e ti ritrovi
tre ticket in più.

### `app/main.py` — gli endpoint

Tre endpoint, tutti in lettura. Guarda `get_ticket`: se il database risponde `None`,
alziamo un `HTTPException` con **404**. Un id che non esiste non è un errore del server:
è una richiesta legittima a cui si risponde "non trovato".

**Come verifico** (rispondi a queste, non serve scrivere niente)

1. Nel browser: `.../tickets/2` → cosa vedi? E `.../tickets/99`?
2. `.../tickets/pippo` → che numero ti risponde? Chi l'ha deciso, visto che nel codice
   non c'è nessun controllo su `pippo`?
3. In `db.py`, quante funzioni servono al database per **scrivere** un ticket? Contale.
   (Risposta: zero. Le scrivi tu adesso.)

---

## Passo 3 — Creare: `POST /tickets`

Adesso l'API impara a scrivere. Servono due pezzi: la funzione che parla col database,
e l'endpoint che la usa.

### 3a. In `app/db.py`

Aggiungi questa funzione **subito prima** di `def _now()`:

```python
def create_ticket(title: str, description: str, status: str) -> dict:
    """Inserisce un nuovo ticket e restituisce il ticket appena creato.

    lastrowid e' l'id che SQLite ha assegnato alla riga appena inserita:
    lo usiamo per rileggere il ticket completo, con id e created_at.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO tickets (title, description, status, created_at) VALUES (?, ?, ?, ?)",
            (title, description, status, _now()),
        )
        new_id = cursor.lastrowid

    return get_ticket(new_id)
```

Quattro `?`, quattro valori. Mai una f-string.

### 3b. In `app/main.py`

Cambia la riga dell'import dei modelli, aggiungendo `TicketIn`:

```python
from app.models import TicketIn, TicketOut
```

Poi aggiungi questo endpoint **in fondo al file**:

```python
@app.post("/tickets", response_model=TicketOut, status_code=201)
def create_ticket(ticket: TicketIn):
    """Crea un nuovo ticket.

    "ticket: TicketIn" dice a FastAPI: prendi il JSON che arriva, controllalo
    contro il modello, e se non va bene rispondi 422 senza nemmeno chiamarmi.
    """
    return db.create_ticket(ticket.title, ticket.description, ticket.status)
```

`status_code=201` perché 201 vuol dire "creato", mentre 200 vuol dire solo "ok".

Salva. Il terminale dice `Reloading...` e poi `Application startup complete`.

**Come verifico** (tutto da `/docs`, ricarica la pagina)

1. `POST /tickets` → Try it out → body `{"title": "Proiettore aula 1 non parte", "description": "Schermo blu"}` → Execute → **201** e il ticket con l'id nuovo.
2. `GET /tickets` → **200**, adesso ce ne sono quattro.
3. `POST /tickets` con `{"title": "ab"}` → **422** e il messaggio `String should have at least 3 characters`.
4. `POST /tickets` con `{"title": "Mouse rotto", "status": "boh"}` → **422**: lo stato non è tra i tre ammessi.
5. **Il test che conta**: `CTRL+C` nel terminale di uvicorn, rilancia `uvicorn app.main:app --reload`, rifai `GET /tickets` → **il ticket che hai creato c'è ancora**. È su disco, non in memoria.

---

## Passo 4 — Modificare e cancellare: `PUT`, `DELETE`, 404

### 4a. In `app/db.py`

Aggiungi queste due funzioni dopo `create_ticket`:

```python
def update_ticket(ticket_id: int, title: str, description: str, status: str) -> Optional[dict]:
    """Modifica un ticket esistente. Restituisce None se quell'id non esiste.

    rowcount dice quante righe sono state modificate: se e' 0, l'id non c'era.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE tickets SET title = ?, description = ?, status = ? WHERE id = ?",
            (title, description, status, ticket_id),
        )
        if cursor.rowcount == 0:
            return None

    return get_ticket(ticket_id)


def delete_ticket(ticket_id: int) -> bool:
    """Cancella un ticket. Restituisce True se c'era, False se l'id non esisteva."""
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
        return cursor.rowcount > 0
```

### 4b. In `app/main.py`

Aggiungi in fondo:

```python
@app.put("/tickets/{ticket_id}", response_model=TicketOut)
def update_ticket(ticket_id: int, ticket: TicketIn):
    """Sostituisce un ticket esistente con i dati che arrivano."""
    updated = db.update_ticket(ticket_id, ticket.title, ticket.description, ticket.status)
    if updated is None:
        raise HTTPException(status_code=404, detail="Ticket non trovato")
    return updated


@app.delete("/tickets/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: int):
    """Cancella un ticket. 204 vuol dire "fatto, e non ho niente da dirti"."""
    if not db.delete_ticket(ticket_id):
        raise HTTPException(status_code=404, detail="Ticket non trovato")
```

Nota che il controllo del 404 è lo stesso di `get_ticket`: se il database dice
"non c'era", l'API risponde 404. Sempre la stessa forma.

**Come verifico** (da `/docs`)

1. `PUT /tickets/1` con `{"title": "Stampante piano 2 offline", "status": "chiuso"}` → **200** e lo stato aggiornato.
2. `GET /tickets/1` → lo stato è `chiuso`.
3. `PUT /tickets/999` con un titolo qualsiasi → **404** `Ticket non trovato`.
4. `DELETE /tickets/3` → **204**, nessun corpo nella risposta.
5. `DELETE /tickets/3` una seconda volta → **404**: adesso non c'è più.
6. `GET /tickets` → il ticket 3 è sparito, gli altri ci sono.

---

## Passo 5 — Filtrare: `GET /tickets?status=aperto`

Chi usa il portale vuole vedere solo i ticket aperti. Aggiungiamo un **query parameter**.

### 5a. In `app/db.py` sostituisci `list_tickets` con:

```python
def list_tickets(status: Optional[str] = None) -> list[dict]:
    """Restituisce i ticket, dal piu' vecchio al piu' recente.

    Se "status" e' None restituisce tutti i ticket, altrimenti solo quelli
    con quello stato.
    """
    with get_connection() as conn:
        if status is None:
            rows = conn.execute("SELECT * FROM tickets ORDER BY id").fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM tickets WHERE status = ? ORDER BY id", (status,)
            ).fetchall()

    return [dict(row) for row in rows]
```

### 5b. In `app/main.py`

Aggiungi agli import in alto:

```python
from typing import Optional

from fastapi import FastAPI, HTTPException, Query

from app.models import TicketIn, TicketOut, TicketStatus
```

(le righe `from fastapi import ...` e `from app.models import ...` **sostituiscono** quelle che c'erano).
Poi sostituisci l'endpoint `GET /tickets` con:

```python
@app.get("/tickets", response_model=list[TicketOut])
def list_tickets(status: Optional[TicketStatus] = Query(default=None)):
    """La lista dei ticket, eventualmente filtrata per stato."""
    return db.list_tickets(status)
```

**Come verifico**

1. Nel browser: `.../tickets?status=aperto` → solo gli aperti. `.../tickets?status=chiuso` → solo i chiusi. `.../tickets` → tutti.
2. `.../tickets?status=boh` → **422**: `TicketStatus` ammette solo tre valori.
3. `.../tickets?status=' OR '1'='1` → **422**. E anche se passasse la validazione, il `?` nella
   query lo tratterebbe come testo da cercare, non come comando. **Due difese, non una.**

---

## Passo 6 — Difendersi: la chiave `X-API-Key`

Leggere è libero. Scrivere solo con la chiave. La chiave **non sta nel codice**: sta in una variabile d'ambiente.

### 6a. Il file `.env`

Nel terminale (il secondo, non quello di uvicorn):

```bash
cp .env.example .env
```

Apri `.env` e cambia il valore: `API_KEY=una-frase-lunga-che-sai-solo-tu`. Salva.
`.env` è nel `.gitignore`: **non** verrà mai committato. `.env.example` sì, ma è vuoto di segreti.

### 6b. In `app/main.py`

Import in alto (aggiungi `os` e `dotenv`, e allarga quello di fastapi):

```python
import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Query
```

Subito dopo gli import, **prima** di `app = FastAPI(...)`:

```python
load_dotenv()
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("Manca API_KEY: copia .env.example in .env e imposta una chiave.")
```

Dopo `db.seed_if_empty()`, la **guardia**:

```python
def require_api_key(x_api_key: Optional[str] = Header(default=None)):
    """Lascia passare solo chi presenta la chiave giusta.

    Il nome "x_api_key" diventa l'header "X-API-Key": FastAPI converte
    gli underscore in trattini da solo.
    """
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

## Passo 7 — Test finale: l'API ricorda e si difende

Spunta tutto. Se una riga non è verde, torna al passo indicato.

| Test | Come | Atteso | Passo |
|------|------|--------|-------|
| Ricorda | riavvia uvicorn, `GET /tickets` | i ticket ci sono ancora | 3 |
| Rifiuta dati sbagliati | `POST` con `{"title": "ab"}` (con chiave) | **422** | 3 |
| Rifiuta stati inventati | `POST` con `"status": "boh"` | **422** | 3 |
| Non esiste → 404 | `GET /tickets/9999` | **404** | 4 |
| Cancella davvero | `DELETE` due volte lo stesso id | **204** poi **404** | 4 |
| Filtra | `?status=aperto` | solo gli aperti | 5 |
| Injection nel filtro | `?status=' OR '1'='1` | **422**, nessun dato extra | 5 |
| Injection nel body | `POST` con `{"title": "x'); DROP TABLE tickets; --"}` (con chiave) | **201**, salvato come testo, poi `GET /tickets` funziona ancora | 3 |
| Senza chiave | `POST` senza `x-api-key` | **401** | 6 |
| Chiave sbagliata | `DELETE /tickets/1` con chiave `abc` | **401** | 6 |
| Segreti fuori dal repo | `git status` | `.env` e `tickets.db` non compaiono | 6 |

L'ultima riga dell'injection nel body è quella da guardare con attenzione: il ticket **viene creato**,
con quel titolo assurdo dentro. Non è un bug. Il `?` ha fatto il suo lavoro: quel testo è finito
nel database come **testo**, non come comando. La tabella è ancora lì.

Poi salva il lavoro:

```bash
git add .
git commit -m "Portale ticket v1: CRUD, validazione, filtro, API key"
git push
```

**Come verifico:** su GitHub, nel tuo repo, vedi `app/db.py` e `app/main.py` con le funzioni nuove.
**Non** vedi `.env` né `tickets.db`.

Domani questa API va online e ci mettiamo davanti una pagina web.

---

## Se ti perdi

- Chiedi. La soluzione completa ce l'ha il docente: serve per **confrontare**, non per copiare, perché domani riparti dal tuo codice.
- Gli errori tipici li raccogliamo insieme negli ultimi 30 minuti: diventano domande della verifica.
