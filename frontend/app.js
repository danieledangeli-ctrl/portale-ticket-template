// app.js — la logica della pagina. Parte VUOTO: lo scriviamo insieme durante la mattina,
// seguendo G2_02 (leggere), G2_03 (scrivere) e G2_04 (CORS e configurazione).

// ---- Riferimenti agli elementi della pagina (gli id di index.html) ----
const messageBox = document.getElementById("message");
const ticketRows = document.getElementById("ticket-rows");
const statusFilter = document.getElementById("status-filter");
const ticketForm = document.getElementById("ticket-form");
const submitButton = document.getElementById("submit-button");

// Se vedi questa riga nella console (F12), il file e' collegato bene.
console.log("app.js caricato. API:", API_URL);
