# Portale Assistenza — trova le falle e chiudile

**"L'app funziona. Ma è piena di buchi."**

Hai un portale ticket completo: si apre, mostra le segnalazioni, ne crea di nuove.
Sembra a posto. Non lo è. Dentro ci sono **cinque punti deboli** e **un pezzo mancante**.

Il tuo lavoro non è costruire da zero: è quello che si fa davvero in azienda, cioè
prendere codice che gira, capire dove è fragile, e ripararlo.

Ogni passo ha tre momenti:
- **Attacca** — fai il danno con le tue mani, così vedi che il buco è vero.
- **Guarda** — cosa è successo, e perché.
- **Ripara** — poche righe. Poi **riattacca**: non deve più funzionare.

> **Come si avvia** (una volta sola, poi resta acceso):
> - Backend: nel terminale, `uvicorn app.main:app --reload`
> - Frontend: in un **secondo** terminale, `cd frontend && python3 -m http.server 5500`, poi apri `http://127.0.0.1:5500`
> - La chiave per scrivere te la dà il docente (è scritta alla lavagna).

Se ti blòcchi su un passo per più di dieci minuti, apri il triangolino **"Serve una mano"**
in fondo al passo: ti dice **dove** guardare, non la soluzione.

---

## Passo 1 — Il filtro che mostra troppo

**Attacca.** Nella pagina, in alto a destra dell'elenco, c'è il menu "Mostra". Sceglie
quali ticket vedere. Ora aprilo dal browser a mano: nella barra dell'indirizzo del
**backend** (porta 8000, non la pagina) scrivi:

```
http://127.0.0.1:8000/tickets?status=aperto
```

Vedi solo gli aperti. Giusto. Adesso prova questo al posto di `aperto`:

```
http://127.0.0.1:8000/tickets?status=x' OR '1'='1
```

**Guarda.** Chiedevi uno stato che non esiste (`x`), e invece di darti zero ticket
te li ha dati **tutti**. Il filtro è stato scavalcato. Apri `app/db.py`, funzione
`list_tickets`: la query viene **costruita incollando** il testo che arriva
dall'utente. Chi scrive nel filtro non sta scegliendo uno stato: sta scrivendo un
pezzo della tua query. Questo è l'**SQL injection**.

**Ripara.** Il valore non deve essere incollato nella stringa, ma passato a parte
con il segnaposto `?`. Così il database lo tratta come un **dato**, mai come codice.

**Riattacca.** Rilancia lo stesso indirizzo con `x' OR '1'='1`: ora restituisce
zero ticket, perché nessuno ha davvero quello stato. Il filtro onesto continua a funzionare.

<details><summary>Serve una mano</summary>

`app/db.py`, `list_tickets`. Guarda com'è già scritta la query di `get_ticket` poco
sotto: usa `?` e una tupla. Il filtro va scritto allo stesso modo:
`"... WHERE status = ? ORDER BY id", (status,)`.
</details>

---

## Passo 2 — Il form che accetta qualsiasi cosa

**Attacca.** Nel form della pagina prova a creare una segnalazione con il **titolo vuoto**.
Passa. Poi, dalla documentazione del backend (`http://127.0.0.1:8000/docs`, endpoint
`POST /tickets`, "Try it out"), manda un ticket con `"status": "banana"`.

**Guarda.** Ricarica l'elenco: c'è una riga senza titolo, e una con uno stato che il
tuo portale non sa neanche colorare. Il database si sta riempiendo di roba senza senso.
Apri `app/main.py`, `create_ticket`: prende il JSON e lo salva **così com'è**, senza
controllare niente.

**Ripara.** Esiste già un modello, `TicketIn` in `app/models.py`, che dice com'è fatto
un ticket valido (titolo da 3 a 100 caratteri, stato solo fra i tre ammessi). Basta
dire a FastAPI di usarlo: cambia la firma della funzione perché riceva un `TicketIn`,
e lascia che sia lui a rispondere **422** quando i dati non vanno.

**Riattacca.** Titolo vuoto → **422**, `status: "banana"` → **422**. Un ticket vero
passa ancora.

<details><summary>Serve una mano</summary>

Confronta con `POST` della soluzione o con il modo in cui `get_ticket` dichiara i suoi
parametri. La firma diventa `def create_ticket(ticket: TicketIn):` e dentro usi
`ticket.title`, `ticket.description`, `ticket.status`. Sparisce il `request.json()`.
</details>

---

## Passo 3 — La cancellazione che non chiede niente

**Attacca.** Creare un ticket chiede la chiave. Cancellarne uno, no. Provalo: dalla
documentazione (`/docs`, `DELETE /tickets/{id}`) cancella il ticket 1 **senza** mettere
nessuna chiave. Sparisce.

**Guarda.** Leggere è giusto che sia libero. Ma **cancellare** è una scrittura, e le
scritture le protegge la chiave. In `app/main.py` guarda `POST`: ha
`dependencies=[Depends(require_api_key)]`. `DELETE`, sotto, **non ce l'ha**.

**Ripara.** Aggiungi la stessa guardia al `DELETE`. Una riga, copiata da `POST`.

**Riattacca.** `DELETE` senza chiave → **401**. Con la chiave giusta → cancella.

<details><summary>Serve una mano</summary>

`app/main.py`, riga di `@app.delete(...)`. Aggiungi `, dependencies=[Depends(require_api_key)]`
dentro le parentesi del decoratore, esattamente come su `@app.post`.
</details>

---

## Passo 4 — Il pezzo che manca: cambiare stato

**Attacca.** Nell'elenco, cambia lo stato di un ticket con il menu colorato. In basso
compare un errore. Apri la console (F12): il server ha risposto **405**.

**Guarda.** Il menu chiama `PUT /tickets/{id}`, ma quell'endpoint **non esiste**: in
`app/main.py` c'è solo un commento `# TODO`. `405` vuol dire "quel metodo qui non c'è".
Questa non è una falla: è codice da scrivere. La funzione che tocca il database,
`update_ticket`, esiste già in `db.py`: manca solo l'endpoint che la usa.

**Ripara.** Scrivi `PUT /tickets/{ticket_id}`. Prendi `POST` come modello: stessa
protezione con la chiave, stesso `TicketIn` in ingresso (il passo 2!), ma chiama
`db.update_ticket(...)` e risponde **404** se quell'id non c'è.

**Riattacca.** Cambia stato dalla pagina: la pastiglia cambia colore, niente errore.

<details><summary>Serve una mano</summary>

Struttura:
```
@app.put("/tickets/{ticket_id}", response_model=TicketOut, dependencies=[Depends(require_api_key)])
def update_ticket(ticket_id: int, ticket: TicketIn):
    aggiornato = db.update_ticket(ticket_id, ticket.title, ticket.description, ticket.status)
    if aggiornato is None:
        raise HTTPException(status_code=404, detail="Ticket non trovato")
    return aggiornato
```
</details>

---

## Passo 5 — Il dato che diventa codice (XSS)

**Attacca.** Crea una segnalazione con questo **titolo** esatto:

```
<img src=x onerror="alert('bucato')">
```

**Guarda.** Appena l'elenco si ricarica, parte un popup. Tu volevi scrivere un titolo,
e il browser ha eseguito il tuo testo come **codice**. Immagina che al posto di
`alert` ci fosse qualcosa che ruba la sessione di chi apre la pagina. Apri
`frontend/app.js`, `costruisciRiga`: il titolo viene messo nella pagina con `innerHTML`,
che dice al browser "questo è HTML, eseguilo".

**Ripara.** Il titolo e la descrizione vanno messi con `textContent`, che dice al
browser "questo è **testo**, mostralo e basta". Serve creare i due `<div>` a mano e
riempirli con `textContent` invece di comporre una stringa di HTML.

**Riattacca.** Ricarica: quel ticket ora si **vede scritto**, `<img ...>` compreso,
e nessun popup. Il dato è tornato a essere un dato.

<details><summary>Serve una mano</summary>

`frontend/app.js`, dentro `costruisciRiga`, il blocco `cellaTesto.innerHTML = ...`.
Sostituiscilo creando due `div` (`document.createElement("div")`), dando a ciascuno
la sua classe (`cella-titolo`, `cella-descrizione`) e assegnando `.textContent = ticket.title`
e `.textContent = ticket.description`. Confronta con la soluzione del docente.
</details>

---

## Passo 6 — Il segreto che non è segreto

**Guarda** (questo è da leggere, non da attaccare). Apri `app/main.py`: la chiave è
**scritta lì dentro**, in chiaro: `API_KEY = "chiave-del-corso-2026"`. E apri
`.gitignore`: il file `.env` **non c'è**. Vuol dire che se pubblichi questo repo su
GitHub, chiunque legge la tua chiave in due clic.

**Ripara**, due mosse:
1. La chiave non sta nel codice ma in una **variabile d'ambiente**: si legge con
   `os.getenv("API_KEY")`, e il valore vero sta nel file `.env` (che hai già).
2. Aggiungi `.env` al `.gitignore`, così quel file **non finisce mai** nel repo.

**Come verifico.** In `main.py` non c'è più nessuna chiave scritta a mano. `.env` è
elencato nel `.gitignore`. L'app parte ancora (legge la chiave dall'ambiente).

<details><summary>Serve una mano</summary>

`API_KEY = os.getenv("API_KEY")` in cima, come nella soluzione, con il controllo
"se manca, fermati". In `.gitignore`, una riga con `.env`. Il `load_dotenv()` che
carica il file c'è già.
</details>

---

## Chiusura — il giro completo

Riparate tutte, rifai i cinque attacchi di fila. Devono fallire tutti:

- [ ] filtro `x' OR '1'='1` → zero ticket, non tutti
- [ ] titolo vuoto / `status: banana` → 422
- [ ] `DELETE` senza chiave → 401
- [ ] menu dello stato → funziona, niente 405
- [ ] titolo `<img ...>` → si vede scritto, niente popup
- [ ] chiave fuori dal codice, `.env` nel `.gitignore`

Poi due righe: **quale falla ti ha sorpreso di più, e perché.**
