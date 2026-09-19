# Portale Assistenza — versione da riparare

Questo è il repo che aprono **gli studenti**. È un portale ticket **completo e funzionante**,
con dentro cinque falle di sicurezza e un endpoint mancante, da trovare e chiudere.

Le istruzioni passo-passo sono in **[`CONSEGNA.md`](./CONSEGNA.md)**.

## Come si avvia

Servono due terminali.

**1. Il backend (l'API):**
```
uvicorn app.main:app --reload
```
Risponde su `http://127.0.0.1:8000`. La documentazione interattiva è su `/docs`.

**2. Il frontend (la pagina):**
```
cd frontend
python3 -m http.server 5500
```
Apri `http://127.0.0.1:5500`.

> Non aprire `index.html` con doppio clic: da `file://` il browser blocca le chiamate
> all'API. Serve il server statico qui sopra.

La **chiave** per creare, modificare ed eliminare te la dà il docente.

## Cosa c'è dentro

```
app/            l'API (FastAPI + SQLite)
  main.py       gli endpoint
  db.py         tutto quello che tocca il database
  models.py     la forma di un ticket valido
frontend/       la pagina (HTML/CSS/JS, senza framework)
  config.js     l'UNICO posto con l'indirizzo dell'API
.env            la chiave (vedi passo 6 della CONSEGNA…)
```

I dati sono di esempio e si ricreano a ogni riavvio del server.
