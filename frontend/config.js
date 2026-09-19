// ============================================================================
// config.js — L'UNICO posto dove sta scritto l'indirizzo dell'API.
// ============================================================================
// Perche' un file solo per una riga? Perche' questo indirizzo cambia tre volte:
// quando lavori in locale, quando passi all'API del docente, quando pubblichi
// la tua su Render. Se fosse sparso dentro app.js, ogni volta lo cercheresti.
//
// Niente barra finale: gli indirizzi si compongono come API_URL + "/tickets".

const API_URL = "http://127.0.0.1:8000";

// Quando pubblicherai la tua API su Render, qui ci andra' il suo indirizzo:
// const API_URL = "https://portale-ticket-tuonome.onrender.com";
