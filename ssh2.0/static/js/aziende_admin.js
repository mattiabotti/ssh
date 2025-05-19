document.addEventListener('DOMContentLoaded', function() {
    // Carica le aziende
    loadAziende();
    
    // Gestione del modal
    const modal = document.getElementById('azienda-modal');
    const span = document.getElementsByClassName('close')[0];
    
    span.onclick = function() {
        modal.style.display = 'none';
    }
    
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
    
    // Evento per aggiungere nuova azienda
    document.getElementById('add-azienda-btn').addEventListener('click', function() {
        resetAziendaForm();
        modal.style.display = 'block';
    });
    
    // Evento per salvare azienda
    document.getElementById('azienda-form').addEventListener('submit', function(e) {
        e.preventDefault();
        saveAzienda();
    });
    
    // Evento per inviare email
    document.getElementById('send-emails-btn').addEventListener('click', function() {
        if (confirm('Sei sicuro di voler inviare email a tutte le aziende?')) {
            sendEmails();
        }
    });
    
    // Evento per applicare filtri
    document.getElementById('apply-filters').addEventListener('click', function() {
        loadAziende();
    });
});

function loadAziende() {
    // Prendi i valori dei filtri
    const statoFilter = document.getElementById('filter-stato').value;
    const comuneFilter = document.getElementById('filter-comune').value;
    
    // Costruisci l'URL con i filtri
    let url = '/get-aziende-admin';
    if (statoFilter || comuneFilter) {
        url += '?';
        if (statoFilter) {
            url += 'stato=' + encodeURIComponent(statoFilter);
        }
        if (comuneFilter) {
            if (statoFilter) url += '&';
            url += 'comune=' + encodeURIComponent(comuneFilter);
        }
    }
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('aziende-tbody');
            tbody.innerHTML = '';
            
            data.aziende.forEach(azienda => {
                const row = document.createElement('tr');
                
                row.innerHTML = `
                    <td>${azienda.nome}</td>
                    <td>${azienda.comune}</td>
                    <td>${azienda.nome_referente || ''}</td>
                    <td>${azienda.email_referente || ''}</td>
                    <td>${getStatoLabel(azienda.stato)}</td>
                    <td>
                        <button class="edit-btn" data-id="${azienda.id}">Modifica</button>
                    </td>
                `;
                
                tbody.appendChild(row);
            });
            
            // Aggiungi event listener ai bottoni di modifica
            document.querySelectorAll('.edit-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    const id = this.getAttribute('data-id');
                    editAzienda(id, data.aziende.find(a => a.id == id));
                });
            });
        })
        .catch(error => console.error('Errore nel caricamento delle aziende:', error));
}

function getStatoLabel(stato) {
    const stati = {
        'da_contattare': 'Da contattare',
        'contattata': 'Contattata',
        'disponibile': 'Disponibile',
        'non_disponibile': 'Non disponibile'
    };
    return stati[stato] || stato;
}

function editAzienda(id, azienda) {
    document.getElementById('azienda-id').value = id;
    document.getElementById('azienda-nome').value = azienda.nome;
    document.getElementById('azienda-indirizzo').value = azienda.indirizzo;
    document.getElementById('azienda-cap').value = azienda.cap || '';
    document.getElementById('azienda-comune').value = azienda.comune;
    document.getElementById('azienda-referente').value = azienda.nome_referente || '';
    document.getElementById('azienda-email').value = azienda.email_referente || '';
    document.getElementById('azienda-telefono').value = azienda.telefono_referente || '';
    document.getElementById('azienda-stato').value = azienda.stato;
    document.getElementById('azienda-disponibilita').checked = azienda.disponibilita_estiva == 1;
    document.getElementById('azienda-osservazioni').value = azienda.osservazioni || '';
    
    document.getElementById('azienda-modal').style.display = 'block';
}

function resetAziendaForm() {
    document.getElementById('azienda-id').value = '';
    document.getElementById('azienda-form').reset();
    document.getElementById('azienda-stato').value = 'da_contattare';
}

function saveAzienda() {
    const aziendaData = {
        id: document.getElementById('azienda-id').value,
        nome: document.getElementById('azienda-nome').value,
        indirizzo: document.getElementById('azienda-indirizzo').value,
        cap: document.getElementById('azienda-cap').value,
        comune: document.getElementById('azienda-comune').value,
        nome_referente: document.getElementById('azienda-referente').value,
        email_referente: document.getElementById('azienda-email').value,
        telefono_referente: document.getElementById('azienda-telefono').value,
        stato: document.getElementById('azienda-stato').value,
        disponibilita_estiva: document.getElementById('azienda-disponibilita').checked ? 1 : 0,
        osservazioni: document.getElementById('azienda-osservazioni').value
    };
    
    fetch('/update-azienda', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(aziendaData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Azienda salvata con successo');
            document.getElementById('azienda-modal').style.display = 'none';
            loadAziende();
        } else {
            alert('Errore: ' + (data.error || 'Si è verificato un errore'));
        }
    })
    .catch(error => {
        console.error('Errore nel salvataggio dell\'azienda:', error);
        alert('Errore nel salvataggio dell\'azienda');
    });
}

function sendEmails() {
    fetch('/send-email', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`Email inviate con successo!\nInviate: ${data.results.sent}\nErrori: ${data.results.errors}\nTotale: ${data.results.total}`);
            loadAziende();
        } else {
            alert('Errore: ' + (data.error || 'Si è verificato un errore'));
        }
    })
    .catch(error => {
        console.error('Errore nell\'invio delle email:', error);
        alert('Errore nell\'invio delle email');
    });
}