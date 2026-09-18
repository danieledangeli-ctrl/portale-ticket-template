"""
Tutto quello che tocca il database sta qui dentro, e solo qui.

Perche' separare? Perche' in "main.py" vogliamo leggere gli endpoint dell'API
senza vedere il SQL di mezzo. Se domani cambiamo database, cambiamo solo questo file.

REGOLA DI SICUREZZA, vale per ogni query di questo file e per quelle che scriverai tu:
i valori che arrivano da fuori si passano SEMPRE con i "?", mai incollandoli
dentro la stringa SQL con le f-string. E' la difesa contro la SQL injection.

    GIUSTO:    conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    SBAGLIATO: conn.execute(f"SELECT * FROM tickets WHERE id = {ticket_id}")
"""

import sqlite3
from datetime import datetime, timezone
from typing import Optional

# Il database e' un singolo file, creato nella cartella del progetto.
# E' nel .gitignore: non finisce su GitHub.
DB_PATH = "tickets.db"

# Ticket di esempio, inseriti al primo avvio (vedi seed_if_empty).
# Servono per avere subito qualcosa da vedere e, piu' avanti, da filtrare.
SEED_TICKETS = [
    ("Stampante del piano 2 offline", "Non compare piu' tra le stampanti disponibili.", "aperto"),
    ("Wi-Fi lento in aula 3", "Dalle 14 in poi la connessione cade di continuo.", "in_lavorazione"),
    ("Monitor da sostituire", "Il monitor della postazione 7 ha una riga verde fissa.", "chiuso"),
]


def get_connection() -> sqlite3.Connection:
    """Apre una connessione al database.

    row_factory = sqlite3.Row fa si' che le righe si leggano per nome di colonna
    (row["title"]) invece che per posizione (row[1]): molto piu' difficile sbagliare.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Crea la tabella dei ticket, se non esiste gia'.

    "IF NOT EXISTS" rende la funzione ripetibile: puoi chiamarla a ogni avvio
    del server senza distruggere i dati gia' presenti.
    """
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


def seed_if_empty() -> int:
    """Inserisce i ticket di esempio, ma solo se la tabella e' vuota.

    Il controllo "solo se vuota" e' importante: senza, a ogni riavvio del server
    ti ritroveresti tre ticket in piu'.

    Restituisce quanti ticket ha inserito (0 se c'erano gia' dei dati).
    """
    with get_connection() as conn:
        already_there = conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
        if already_there > 0:
            return 0

        created_at = _now()
        conn.executemany(
            "INSERT INTO tickets (title, description, status, created_at) VALUES (?, ?, ?, ?)",
            [(title, description, status, created_at) for title, description, status in SEED_TICKETS],
        )

    return len(SEED_TICKETS)


def list_tickets() -> list[dict]:
    """Restituisce tutti i ticket, dal piu' vecchio al piu' recente."""
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM tickets ORDER BY id").fetchall()

    # Le righe di sqlite3 non sono dizionari: le convertiamo perche' FastAPI
    # possa trasformarle in JSON.
    return [dict(row) for row in rows]


def get_ticket(ticket_id: int) -> Optional[dict]:
    """Restituisce un singolo ticket, oppure None se quell'id non esiste.

    Optional[dict] si legge: "un dizionario, oppure niente".
    """
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()

    return dict(row) if row else None


def _now() -> str:
    """Data e ora di adesso, in formato testo (es. "2026-09-18T10:30:00+00:00").

    L'underscore davanti al nome e' una convenzione Python: "funzione di servizio,
    usata solo dentro questo file".
    """
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
