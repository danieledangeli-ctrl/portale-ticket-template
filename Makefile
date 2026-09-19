# Accende i due pezzi del portale. Servono DUE terminali:
#   Terminale 1:  make backend
#   Terminale 2:  make frontend
# Lasciali aperti tutti e due: se ne chiudi uno, meta' portale smette di funzionare.
#
# In LOCALE (sul tuo computer), la prima volta:  make setup
# Su Codespaces non serve: le librerie ci sono gia'.

.PHONY: help setup backend frontend

# Se c'e' un ambiente locale (.venv) usa quello; altrimenti il python di sistema
# (e' il caso di Codespaces, dove le librerie sono gia' installate).
PY := $(shell [ -x .venv/bin/python ] && echo .venv/bin/python || echo python3)

# "make" senza argomenti mostra questo aiuto.
help:
	@echo "make setup     -> prepara l'ambiente in locale (una volta sola)"
	@echo "make backend   -> accende l'API      su http://localhost:8000  (terminale 1)"
	@echo "make frontend  -> accende la pagina  su http://localhost:5500  (terminale 2)"
	@echo ""
	@echo "Servono due terminali, uno per comando. Lasciali aperti."

# Solo in locale: crea l'ambiente virtuale e installa le librerie.
setup:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	@echo ""
	@echo "Pronto. Ora: make backend"

# L'API (FastAPI). --reload = si riavvia da sola quando salvi un file.
backend:
	$(PY) -m uvicorn app.main:app --reload

# La pagina (un server statico). Da file:// il browser blocca le chiamate: serve questo.
frontend:
	cd frontend && $(PY) -m http.server 5500
