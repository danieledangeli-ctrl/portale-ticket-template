# Portale Assistenza — la versione da riparare

## Cos'è questa roba

Un **portale interno di segnalazioni**: il posto dove in un'azienda scrivi "la stampante
del piano 2 non stampa" e qualcuno lo prende in carico.

Funziona. Si apre, mostra le segnalazioni, ne crea di nuove, le filtra, cambia lo stato.
Non devi costruirlo: **ce l'hai già finito**.

Ma è **bucato**. Dentro ci sono cinque punti deboli veri — quelli che si trovano nel
codice vero — e un pezzo che manca. Il tuo lavoro per due giorni è trovarli e chiuderli.

> Non stai facendo un esercizio da scuola. È quello che si fa in azienda: ti danno codice
> che gira, scritto da altri, e devi capire dove è fragile prima che lo capisca qualcun altro.

**Le istruzioni passo per passo sono in [`CONSEGNA.md`](./CONSEGNA.md).** Parti da lì.

---

## Sono due programmi, non uno

Questa è la cosa da capire prima di toccare qualsiasi tasto.

```
   IL TUO BROWSER
         │
         │  (1) chiede la pagina
         ▼
   ┌──────────────┐          ┌──────────────┐
   │  LA PAGINA   │  (2)     │    L'API     │
   │  porta 5500  │ ───────► │  porta 8000  │
   │              │  chiede  │              │
   │ HTML CSS JS  │ i dati   │ Python +     │
   │              │ ◄─────── │ database     │
   └──────────────┘  JSON    └──────────────┘
      http.server               uvicorn
```

- **L'API** (porta **8000**) è un programma Python. Parla solo JSON: se la apri nel
  browser vedi testo, non un sito. È lei che tiene i dati.
- **La pagina** (porta **5500**) è HTML, CSS e JavaScript. Non ha dati suoi: li **chiede**
  all'API, uno per uno, mentre la guardi.

Girano **separati**, in **due terminali diversi**, e restano accesi tutto il giorno.
Spegnere uno dei due rompe metà delle cose, ed è utile saperlo: quando qualcosa non va,
la prima domanda è sempre *"quale dei due è morto?"*.

---

## Accenderlo

**Terminale 1 — l'API.** Lascialo lì, non chiuderlo.

```bash
uvicorn app.main:app --reload
```

Deve comparire `Application startup complete`. La documentazione automatica dell'API
è su `/docs`: lì puoi provare ogni endpoint senza scrivere codice.

**Terminale 2 — la pagina.** Aprine uno **nuovo** (in VS Code: il `+` nel pannello del
terminale). Il primo resta occupato da `uvicorn`.

```bash
cd frontend
python3 -m http.server 5500
```

**Poi apri la pagina.** Su Codespaces: pannello **PORTS**, riga della porta **5500**,
clicca sull'icona del mondo. In locale: `http://127.0.0.1:5500`.

> ⚠️ **Non aprire `index.html` con doppio clic.** Da `file://` il browser blocca le
> chiamate all'API per sicurezza, e vedi una pagina vuota senza capire perché.
> Serve il server del terminale 2.

> ⚠️ **Prima che la pagina mostri qualcosa devi dirle dove sta l'API**: si fa in
> `frontend/config.js`, ed è scritto lì dentro cosa mettere. È il passo 0 della consegna.

**La chiave** per creare, modificare ed eliminare te la dà il docente (è alla lavagna).

---

## Cosa c'è dentro

```
app/            l'API (FastAPI + SQLite)
  main.py       gli endpoint: chi risponde a cosa
  db.py         tutto quello che tocca il database
  models.py     la forma di una segnalazione valida
frontend/       la pagina (HTML/CSS/JS, senza framework)
  index.html    la struttura: tabella, form, filtro
  style.css     l'aspetto
  app.js        la logica: sei sezioni numerate e commentate
  config.js     l'UNICO posto con l'indirizzo dell'API
.env            la chiave. Guardalo bene. E guarda il .gitignore…
requirements.txt  le librerie che servono
```

I dati sono di esempio e si ricreano da soli a ogni avvio: puoi rompere tutto senza paura.

---

## Le due giornate

**Oggi** chiudi le tre falle che vivono dentro l'API e scrivi il pezzo che manca. Sono
quelle che si vedono da qui, dal tuo Codespace.

**Domani** il portale va **online**, con un indirizzo vero e un repo pubblico. Lì si
chiudono le altre due: in locale non farebbero male a nessuno, e capirai perché.
