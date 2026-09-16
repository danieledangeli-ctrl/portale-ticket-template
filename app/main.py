"""
Portale Ticket — punto di partenza.

Questo file contiene il server minimo: un solo endpoint, GET /health,
che risponde "ok". Serve a verificare che l'ambiente funzioni.
Tutto il resto lo costruisci tu seguendo la CONSEGNA.
"""

from fastapi import FastAPI

# L'oggetto "app" e' il server. uvicorn lo cerca con il nome app.main:app
app = FastAPI(title="Portale Ticket", version="0.1")


@app.get("/health")
def health():
    """Risponde se il server e' vivo. Lo useremo anche in G2 per il monitoraggio."""
    return {"status": "ok"}
