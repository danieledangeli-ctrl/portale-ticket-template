"""
Portale Ticket — punto di partenza.

Quello che c'e' gia':
  GET /health          il server e' vivo?
  GET /tickets         la lista dei ticket
  GET /tickets/{id}    un ticket solo, oppure 404 se non esiste

Quello che costruisci tu, seguendo la CONSEGNA:
  POST   /tickets        creare un ticket
  PUT    /tickets/{id}   modificarlo
  DELETE /tickets/{id}   cancellarlo
  il filtro ?status=...  e la chiave X-API-Key sulle scritture

Al primo avvio il database viene creato e riempito con tre ticket di esempio,
cosi' hai subito qualcosa da vedere.
"""

from fastapi import FastAPI, HTTPException

from app import db
from app.models import TicketOut

app = FastAPI(title="Portale Ticket", version="0.2")

# Preparazione del database, una volta sola all'avvio del server:
# prima la tabella, poi i ticket di esempio (solo se la tabella e' vuota).
db.init_db()
db.seed_if_empty()


@app.get("/health")
def health():
    """Risponde se il server e' vivo. Lo useremo anche in G2 per il monitoraggio."""
    return {"status": "ok"}


@app.get("/tickets", response_model=list[TicketOut])
def list_tickets():
    """La lista completa dei ticket.

    response_model=list[TicketOut] dice a FastAPI: "rispondi una lista di ticket".
    Serve anche a generare la documentazione automatica su /docs.
    """
    return db.list_tickets()


@app.get("/tickets/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: int):
    """Un singolo ticket.

    {ticket_id} nel percorso diventa il parametro della funzione. Avendolo dichiarato
    "int", FastAPI rifiuta da solo un URL come /tickets/pippo con un errore 422.
    """
    ticket = db.get_ticket(ticket_id)

    # Un id che non esiste non e' un errore del server: e' un 404, "non trovato".
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket non trovato")

    return ticket
