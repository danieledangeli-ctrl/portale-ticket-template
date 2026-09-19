# Giorno 2 — Portalo online, e difendilo davvero

**Ieri hai chiuso i buchi che stanno nel server.** Oggi il portale esce da questo
computer: va online, con un indirizzo vero e un repo pubblico. E lì si aprono i due
buchi che ieri avevamo lasciato stare — perché in locale non facevano male a nessuno.

Stesso metodo di ieri: **attacca → guarda → ripara → riattacca**.

> **Non si scrive il frontend.** La pagina è già finita dal primo minuto di ieri.
> Oggi si lavora su **come viaggia una richiesta HTTP** e su cosa si rompe quando in
> mezzo c'è internet: un altro dominio, un repo pubblico, un tab Network aperto.

---

# MATTINA

## Passo 0 — Siamo tutti allo stesso punto? (20 min)

> **Si fa insieme.** Prima di andare avanti, ognuno controlla a che punto è il suo
> portale. Non è un voto: è che da qui in poi i passi danno per scontato che ieri sia
> a posto.

Accendi i due server come ieri (`uvicorn` nel primo terminale, `http.server` nel
secondo) e apri un **terzo** terminale. Incolla i quattro comandi **tutti insieme**:

```bash
echo "1. filtro:  $(curl -s -o /dev/null -w '%{http_code}' -G 'http://127.0.0.1:8000/tickets' --data-urlencode "status=x' OR '1'='1")  (deve dire 422)"
echo "2. POST:    $(curl -s -o /dev/null -w '%{http_code}' -X POST 'http://127.0.0.1:8000/tickets' -H 'X-API-Key: chiave-del-corso-2026' -H 'Content-Type: application/json' -d '{"title":"","status":"banana"}')  (deve dire 422)"
echo "3. DELETE:  $(curl -s -o /dev/null -w '%{http_code}' -X DELETE 'http://127.0.0.1:8000/tickets/1')  (deve dire 401)"
echo "4. PUT:     $(curl -s -o /dev/null -w '%{http_code}' -X PUT 'http://127.0.0.1:8000/tickets/2' -H 'X-API-Key: chiave-del-corso-2026' -H 'Content-Type: application/json' -d '{"title":"prova","description":"x","status":"chiuso"}')  (deve dire 200)"
```

**Quattro righe giuste** → hai finito ieri. Aspetta i compagni, o aiuta il vicino.

**Una o più sbagliate** → non è un problema, si recupera in trenta secondi. Nello
stesso terminale, dalla **radice del repo** (dove vedi `app/` e `frontend/`):

```bash
cd /workspaces/*
git fetch origin g1-riparato
git checkout origin/g1-riparato -- app/db.py app/main.py
```

> ⚠️ Questo **sostituisce** i tuoi `app/db.py` e `app/main.py` con la versione
> completa. Se avevi riparato qualcosa, il tuo lavoro in quei due file viene perso —
> è il senso del recupero. Il resto del repo non si tocca.

`uvicorn --reload` si riavvia da solo. Rilancia i quattro comandi: ora devono essere
tutti verdi.

**Come verifico:** 422 · 422 · 401 · 200.

---

## Passo 1 — Come la pagina parla con l'API (45 min)

> Qui non si scrive niente. Si legge, e si guarda il traffico vero.

### 1a. Il file

Apri `frontend/app.js`. È diviso in **sei sezioni numerate**, ognuna con due righe di
commento che dicono cosa fa e quando viene chiamata. Leggile in ordine.

Cerca la funzione che carica l'elenco. Dentro c'è questo, ed è il cuore di tutto:

```js
const risposta = await fetch(API_URL + "/tickets");
if (!risposta.ok) { … }
const dati = await risposta.json();
```

Tre righe, tre cose diverse:

| Riga | Cosa fa |
|------|---------|
| `fetch(...)` | manda la richiesta HTTP e **aspetta** (è quello che fa `await`) |
| `risposta.ok` | è `true` solo per gli status 2xx. Un 404 o un 401 **non** è un errore di rete: è una risposta arrivata benissimo, che dice "no" |
| `risposta.json()` | prende il testo della risposta e lo trasforma in oggetti JavaScript |

### 1b. Il traffico vero

Premi **F12** → scheda **Network** → ricarica la pagina.

Clicca sulla riga `tickets`. Sono le stesse cose che ieri vedevi in `curl`, ma disegnate:

- **Headers** → in alto il metodo (`GET`) e lo status (`200`)
- **Response** → il JSON esatto che è tornato
- **Timing** → quanto ci ha messo

Ora tieni il Network aperto e **crea una segnalazione** col form. Compare una seconda
riga: `POST`, status `201`. Clicca su **Request Headers**: c'è `X-API-Key`, e accanto
**la chiave in chiaro**.

> Guardala bene. Ci torniamo nel pomeriggio.

### 1c. Gli status code, dal lato di chi chiama

Prova a sbagliare apposta, e guarda cosa fa la pagina:

| Cosa fai | Status | Cosa mostra la pagina |
|----------|--------|----------------------|
| Crei senza scrivere la chiave | `401` | "Chiave API sbagliata" |
| Crei con un titolo di due lettere | `422` | il messaggio di validazione |
| In `config.js` aggiungi `/sbagliato` all'URL | `404` | "Errore dal server: 404" |
| In `config.js` metti `https://non-esiste.example` | — | "Impossibile contattare l'API" |

**Rimetti l'URL giusto.**

L'ultima riga è diversa dalle altre tre: lì non è arrivata **nessuna** risposta. Le
prime tre sono risposte arrivate, che dicono di no. Un client serio le distingue —
il tuo `app.js` lo fa con `risposta.ok` e con il `try/catch`.

**Come verifico:** sai dire, per ognuno dei quattro casi, se il server ha risposto o no.

---

## Passo 2 — Il dato che diventa codice (60 min)

**Attacca.** Crea una segnalazione con questo **titolo** esatto:

```
<img src=x onerror="alert('bucato')">
```

**Guarda.** Appena l'elenco si ricarica, parte un popup. Tu volevi scrivere un titolo,
e il browser ha eseguito il tuo testo come **codice**. Si chiama **XSS**.

Al posto di `alert` poteva esserci qualcosa che legge i cookie di chi apre la pagina e
li manda altrove. E non colpisce te: colpisce **chiunque apra il portale** — i tuoi
colleghi, il tuo capo.

Apri `frontend/app.js`, funzione `costruisciRiga`. Il titolo finisce nella pagina con
`innerHTML`, che al browser vuol dire: *"questo è HTML, eseguilo"*.

**Ripara.** Titolo e descrizione vanno messi con `textContent`, che vuol dire:
*"questo è **testo**, mostralo e basta"*. Devi creare i due `<div>` a mano e riempirli,
invece di comporre una stringa di HTML.

**Riattacca.** Ricarica: quel ticket ora si **vede scritto**, `<img ...>` compreso, e
nessun popup. Il dato è tornato a essere un dato.

<details><summary>Serve una mano</summary>

In `costruisciRiga`, il blocco `cellaTesto.innerHTML = ...`. Sostituiscilo creando due
`div` con `document.createElement("div")`, dando a ciascuno la sua classe
(`cella-titolo`, `cella-descrizione`) e assegnando `.textContent = ticket.title` e
`.textContent = ticket.description`.
</details>

### La cosa da capire, che vale più della riparazione

**L'API non ha sbagliato niente.** Ha salvato quel testo e l'ha restituito: è il suo
mestiere, e non è lei a decidere come verrà mostrato. Quello stesso ticket potrebbe
finire in un'app mobile, in un export Excel, in una mail — posti dove `<img>` non
significa niente.

**La difesa sta nel punto in cui il dato diventa HTML.** Cioè nel frontend, nella riga
che hai appena cambiato.

**Regola:** dati che vengono da fuori (API, utente, URL) → `textContent`.
`innerHTML` **solo** con HTML scritto da te, mai con una variabile dentro.

**Come verifico:** il ticket col titolo strano si vede scritto, e non succede niente.

---

## Passo 3 — Andare online (75 min)

Due servizi separati: l'API su **Render**, la pagina su **Netlify**. È come funziona
davvero, e da qui in poi lavori su indirizzi veri.

### 3a. Prima di partire

- [ ] `git add -A && git commit -m "XSS riparato" && git push`
- [ ] Account creati con **Sign up with GitHub** (niente carta): [render.com](https://render.com) e [netlify.com](https://netlify.com)

### 3b. L'API su Render

1. Render → **New → Web Service** → **Connect** al tuo repo (la prima volta autorizzi Render a vedere i tuoi repo)
2. Compila:

   | Campo | Valore |
   |-------|--------|
   | Name | `portale-ticket-<tuonome>` |
   | Region | Frankfurt |
   | Branch | `main` |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
   | Instance Type | **Free** |

3. **Environment Variables** → aggiungi **una sola** variabile:

   | Key | Value |
   |-----|-------|
   | `ALLOWED_ORIGINS` | `*` — per ora. La chiudiamo nel pomeriggio |

   > E la chiave? Non serve. Guarda `app/main.py`: la chiave è **scritta lì dentro**.
   > Finché sta nel codice, una variabile d'ambiente non cambierebbe niente.
   > Tienilo a mente: è il passo 5.

4. **Deploy Web Service**. Guarda scorrere i log: `pip install`, poi `Uvicorn running`. Due o tre minuti.

Perché `--host 0.0.0.0 --port $PORT`: in locale uvicorn ascolta solo il tuo computer
sulla 8000. Su un server deve accettare connessioni **da fuori** (`0.0.0.0`) sulla
porta che decide Render (`$PORT`), non una scelta da te.

**Come verifico**

- In alto c'è il tuo URL, tipo `https://portale-ticket-mario.onrender.com`. Apri `/health` → `{"status":"ok"}`. Apri `/docs`.
- Da `/docs`: `POST /tickets` senza chiave → **401**. Con la chiave → **201**.
- **Guarda l'URL: `https://`.** Non l'hai chiesto, te l'ha dato Render. Prova `http://.../health`: ti redirige. Senza HTTPS, quell'header `X-API-Key` che hai visto stamattina nel Network viaggerebbe **in chiaro** sulla rete — il Wi-Fi del bar, quello del laboratorio — e chiunque in mezzo potrebbe leggerlo.

### 3c. La pagina su Netlify

Prima punta la pagina alla **tua** API. In `frontend/config.js`:

```js
const API_URL = "https://portale-ticket-<tuonome>.onrender.com";
```

Senza barra finale. Salva, commit, push.

Poi: Netlify → **Add new site → Deploy manually**. Ti serve la cartella `frontend/`
sul tuo computer: nel Codespace, tasto destro su `frontend` → **Download**. Se scarica
uno `.zip`, scompattalo. Trascina la cartella nel riquadro di Netlify.

In pochi secondi hai un indirizzo tipo `https://nome-a-caso-123.netlify.app`. Da
**Site configuration → Change site name** chiamalo `portale-ticket-<tuonome>`.

**Come verifico:** apri l'indirizzo Netlify → **il tuo portale è online**. Mandalo a
qualcuno, si apre davvero.

### 3d. Il cold start

Chiudi tutto e vai a pranzo. Alla ripresa, riapri la tua pagina: ci mette
**20–40 secondi** a caricare la prima volta.

Non è rotta. Il piano gratuito di Render **spegne** il servizio quando nessuno lo usa,
e lo riaccende alla prima richiesta. È il primo fenomeno di performance che incontri,
ed è quello che l'utente vede come "il sito è lento". Annotalo: serve al passo 6.

> Stessa ragione per cui il tuo database si svuota: su Render free il disco non è
> permanente, a ogni riavvio i dati ripartono da quelli di esempio. Per il laboratorio
> va bene. Per un portale vero servirebbe un database gestito.

---

# POMERIGGIO

## Passo 4 — CORS: il browser che blocca (60 min)

Stamattina tutto ha funzionato perché `ALLOWED_ORIGINS` è `*`. Adesso vediamo cosa c'è
sotto.

### 4a. Cos'è un'origine

Il browser identifica ogni pagina con la sua **origine** = schema + host + porta:

| URL | Origine |
|-----|---------|
| `https://portale-ticket-mario.netlify.app/index.html` | `https://portale-ticket-mario.netlify.app` |
| `https://portale-ticket-mario.onrender.com/tickets` | `https://portale-ticket-mario.onrender.com` ← **diversa** |

La tua pagina e la tua API sono **sempre** su origini diverse. È la situazione normale,
non un errore di impostazione.

### 4b. La regola

Per la *Same-Origin Policy*, il browser **non lascia leggere** a una pagina la risposta
di un'altra origine, a meno che quel server non l'autorizzi con un header:

```
Access-Control-Allow-Origin: https://portale-ticket-mario.netlify.app
```

Questo meccanismo è **CORS**. Attenzione a chi fa cosa:

- **Il server** dichiara "accetto chiamate da queste origini".
- **Il browser** controlla e, se l'origine non c'è, **butta via la risposta**.
- `curl`, `requests`, Postman **non hanno CORS**: non sono browser.

### 4c. Chiudilo sulla tua pagina

Render → il tuo servizio → **Environment** → modifica:

| Key | Value |
|-----|-------|
| `ALLOWED_ORIGINS` | `https://portale-ticket-<tuonome>.netlify.app` (senza barra finale) |

**Save** → Render rideploya da solo, uno o due minuti.

**Come verifico**

1. La tua pagina Netlify funziona ancora. Ricarica dopo il redeploy.
2. Apri la pagina **del tuo vicino** e, nella sua console (F12), scrivi:
   ```js
   fetch("https://portale-ticket-<iltuonome>.onrender.com/tickets").then(r => r.json()).then(console.log)
   ```
   → errore rosso **CORS**. La tua API non autorizza la sua pagina.
3. Nella scheda Network di quell'errore, guarda lo **status: 200**. L'API **ha risposto**.
   È il browser che ha buttato la risposta.

Leggi due volte il punto 3: è la cosa che sbagliano tutti.

### 4d. Quindi CORS cosa protegge?

Dal terminale, **la stessa chiamata che il browser ha bloccato**:

```bash
curl https://portale-ticket-<tuonome>.onrender.com/tickets
```

Funziona. Senza problemi.

**CORS non protegge la tua API** — `curl` passa lo stesso. **Protegge gli utenti dei
browser**: impedisce a un sito estraneo di usare il browser di una persona per parlare
con la tua API a nome suo.

La chiave protegge le **scritture**. CORS decide chi può **leggere le risposte da una
pagina web**. Sono due cose diverse, e servono tutte e due.

**Come verifico:** sai spiegare perché `curl` passa e il browser no.

---

## Passo 5 — Il segreto che non è segreto (60 min)

### 5a. Guarda

Apri il **tuo** repo su GitHub, dal browser. Vai in `app/main.py`.

```python
API_KEY = "chiave-del-corso-2026"
```

È lì. Pubblica. Col tuo nome sopra. Chiunque la legge in due clic e può scrivere sulla
tua API.

Ora apri `.gitignore`. Cerca `.env`. **Non c'è.** Quindi anche quel file è nel repo.

### 5b. Ripara — e sono tre mosse, non una

**Primo tempo — il futuro.** Che non succeda più.

1. In `.gitignore`, aggiungi una riga: `.env`
2. In `app/main.py`, la chiave non sta più nel codice:
   ```python
   API_KEY = os.getenv("API_KEY")
   if not API_KEY:
       raise RuntimeError("Manca API_KEY: copia .env.example in .env e imposta una chiave.")
   ```
   Il `load_dotenv()` che legge il file `.env` c'è già.

**Secondo tempo — il presente.** Il file è ancora dentro git.

```bash
git rm --cached .env
```

`--cached` lo toglie da git ma **lo lascia sul disco**: l'app continua a girare.

Commit e push.

**Terzo tempo — il passato. È quello che conta.**

Sul tuo repo su GitHub apri il **primo commit**, quello di quando hai creato il repo.
Guarda `app/main.py`.

**La chiave è ancora lì.**

Git non dimentica. `.gitignore` protegge il futuro, `git rm --cached` il presente, ma
la storia dei commit resta, e chiunque la può leggere.

L'unica riparazione vera è **cambiare la chiave**:

1. scegline una nuova e mettila nel tuo `.env` (che ora è ignorato)
2. su Render → **Environment** → aggiungi `API_KEY` con il nuovo valore → **Save**
3. la vecchia chiave, quella nella storia, adesso non apre più niente

> **Un segreto finito su un repo pubblico è bruciato. Non si toglie: si cambia.**

### 5c. E la chiave nel browser?

Ricordi il tab Network di stamattina, con `X-API-Key` in chiaro?

Quella non si può nascondere. La pagina deve mandarla, e chi apre il browser la vede.
**HTTPS protegge il canale, non il segreto**: cifra il viaggio, così nessuno la legge
per strada — ma l'utente che la digita, ovviamente, ce l'ha.

Per questo la pagina la **chiede all'utente** invece di tenerla scritta dentro: una
chiave in un frontend non è un segreto, è un'etichetta. Identifica, non protegge.

Il modo giusto sarebbe un login vero — utenti, password, sessioni — dove il browser
tiene un gettone temporaneo e non la chiave di tutti. Non lo facciamo oggi: la chiave
unica è il primo gradino, non l'ultimo.

**Come verifico:** in `main.py` non c'è nessuna chiave scritta. `.env` è nel
`.gitignore`. Su Render c'è `API_KEY` col valore nuovo. L'app funziona ancora — con la
chiave nuova. E con la vecchia dà **401**.

---

## Passo 6 — Il riattacco (75 min)

Cinque attacchi, sul tuo portale **online**. Devono fallire tutti.

Al posto di `API` metti `https://portale-ticket-<tuonome>.onrender.com`,
al posto di `PAGINA` metti `https://portale-ticket-<tuonome>.netlify.app`.

| # | Attacco | Come | Deve succedere |
|---|---------|------|----------------|
| 1 | SQL injection | `curl -G "API/tickets" --data-urlencode "status=x' OR '1'='1"` | **422** — il filtro non si scavalca |
| 2 | Dati spazzatura | `POST` con titolo vuoto e `status:"banana"`, con la chiave | **422** — il database resta pulito |
| 3 | Scrittura senza chiave | `curl -i -X DELETE "API/tickets/1"` | **401** — e lo stesso per POST e PUT |
| 4 | Il segreto | apri `app/main.py` sul tuo repo, e il **primo commit** | nel file attuale nessuna chiave; nel primo commit c'è la vecchia, **che non funziona più** |
| 5 | XSS | crea un ticket col titolo `<img src=x onerror="alert(1)">` e apri `PAGINA` | si **vede scritto**, nessun popup |

E un sesto, che non è una falla ma va provato:

| 6 | Origine estranea | dalla console di **un'altra** pagina: `fetch("API/tickets")` | errore CORS. Poi lo stesso URL con `curl`: **funziona**. Sai dire perché |

**Se qualcosa non regge**, hai il pomeriggio: torna al passo di ieri o di oggi che lo
riguarda e chiudilo. Il modulo finisce con tutti i test verdi, non con l'orario.

---

## Il report — cinque righe, non di più

Crea `REPORT.md` nel repo, committa e pusha.

```markdown
# Portale Assistenza — report

- API:      https://portale-ticket-<tuonome>.onrender.com
- Pagina:   https://portale-ticket-<tuonome>.netlify.app

## I cinque attacchi
(uno per riga: quale, cosa ha risposto, regge sì/no)

## Il cold start
Quanti secondi ci ha messo la prima richiesta dopo la pausa, e perché.

## La cosa che non sapevo
Una riga. Quella vera.
```

---

## Cosa ti porti a casa

1. Un'API e una pagina sono **due programmi separati** che si parlano via HTTP, e in produzione stanno su due servizi diversi.
2. Un dato che viene da fuori non è mai codice: lo diventa se sei tu a metterlo dove il browser lo esegue.
3. CORS non protegge l'API: protegge gli utenti del browser. La chiave protegge le scritture. Due cose diverse.
4. HTTPS protegge il canale, non il segreto.
5. **Un segreto finito in un repo pubblico è bruciato. Non si toglie: si cambia.**
