# Accende i due pezzi del portale. Servono DUE terminali:
#   Terminale 1:  make backend
#   Terminale 2:  make frontend
# Lasciali aperti tutti e due: se ne chiudi uno, meta' portale smette di funzionare.

.PHONY: help backend frontend

# "make" senza argomenti mostra questo aiuto.
help:
	@echo "make backend   -> accende l'API      su http://localhost:8000  (terminale 1)"
	@echo "make frontend  -> accende la pagina  su http://localhost:5500  (terminale 2)"
	@echo ""
	@echo "Servono due terminali, uno per comando. Lasciali aperti."

# L'API (FastAPI). --reload = si riavvia da sola quando salvi un file.
backend:
	uvicorn app.main:app --reload

# La pagina (un server statico). Da file:// il browser blocca le chiamate: serve questo.
frontend:
	cd frontend && python3 -m http.server 5500
