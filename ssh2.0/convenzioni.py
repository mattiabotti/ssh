#FUNZIONA!
import os
import sqlite3
import tornado.ioloop
import tornado.web
from convenzioni_handler import replace_text_in_docx

DB_FILE = 'db.sqlite3'

def fetch_data_from_db(associazione_id):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            studenti.nome AS STUDENTE,
            aziende.nome AS AZIENDA,
            aziende.via AS VIA,
            aziende.comune AS CITTA_SEDE,
            aziende.nome_referente AS NOME_RAP,
            associazioni.data_inizio AS INIZIO_PERIODO,
            associazioni.data_fine AS FINE_PERIODO
        FROM associazioni
        JOIN studenti ON associazioni.id_studente = studenti.id
        JOIN aziende ON associazioni.id_azienda = aziende.id
        WHERE associazioni.id = ?;
    """, (associazione_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise tornado.web.HTTPError(404, f"Nessuna convenzione trovata per id={associazione_id}")
    return dict(row)

def get_all_associazioni():
    """Recupera tutti gli ID delle associazioni dal database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM associazioni")
    associazioni_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return associazioni_ids

def process_all_convenzioni():
    """Elabora tutte le convenzioni per ogni associazione nel database"""
    template_file = 'template.docx'
    output_dir = 'convenzioni_generate'
    
    # Crea la directory di output se non esiste già
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Ottieni tutti gli ID delle associazioni
    associazioni_ids = get_all_associazioni()
    
    for associazione_id in associazioni_ids:
        try:
            # Preleva i dati per questa associazione
            data = fetch_data_from_db(associazione_id)
            
            # Genera il nome del file di output
            output_file = os.path.join(output_dir, f"{data['AZIENDA']}_convenzione.docx")
            
            # Usa la funzione fornita per sostituire i segnaposto nel template
            replace_text_in_docx(
                template_file,
                output_file,
                {
                    "[[STUDENTE]]": data['STUDENTE'],
                    "[[AZIENDA]]": data['AZIENDA'],
                    "[[VIA]]": data['VIA'],
                    "[[CITTA_SEDE]]": data['CITTA_SEDE'],
                    "[[NOME_RAP]]": data['NOME_RAP'],
                    "[[INIZIO_PERIODO]]": data['INIZIO_PERIODO'],
                    "[[FINE_PERIODO]]": data['FINE_PERIODO']
                }
            )
            
            print(f"Generata convenzione per associazione ID {associazione_id}: {output_file}")
            
        except Exception as e:
            print(f"Errore nella generazione della convenzione per associazione ID {associazione_id}: {str(e)}")

# --- HANDLER HTTP ---
class ConvenzioneHandler(tornado.web.RequestHandler):
    async def get(self):
        action = self.get_argument('action', 'single')
        
        if action == 'all':
            # Elabora tutte le convenzioni
            process_all_convenzioni()
            self.write("Tutte le convenzioni sono state generate nella directory 'convenzioni_generate'")
            return
        
        # Funzionalità originale per una singola convenzione
        convenzione_id = self.get_argument('convenzione_id', None)
        if not convenzione_id:
            raise tornado.web.HTTPError(400, "Parametro 'convenzione_id' obbligatorio quando action non è 'all'")

        try:
            # Preleva dati
            data = fetch_data_from_db(convenzione_id)
            
            # Usa la funzione fornita in convenzioni_handler.py
            template_file = 'template.docx'
            output_file = f"Convenzione_{convenzione_id}.docx"
            
            replacements = {
                "[[STUDENTE]]": data['STUDENTE'],
                "[[AZIENDA]]": data['AZIENDA'],
                "[[VIA]]": data['VIA'],
                "[[CITTA_SEDE]]": data['CITTA_SEDE'],
                "[[NOME_RAP]]": data['NOME_RAP'],
                "[[INIZIO_PERIODO]]": data['INIZIO_PERIODO'],
                "[[FINE_PERIODO]]": data['FINE_PERIODO']
            }
            
            replace_text_in_docx(template_file, output_file, replacements)
            
            # Invia il file come download
            self.set_header('Content-Type',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            self.set_header('Content-Disposition', f'attachment; filename="{output_file}"')
            with open(output_file, 'rb') as f:
                self.write(f.read())
            
            # Rimuovi il file temporaneo dopo l'invio
            if os.path.exists(output_file):
                os.remove(output_file)
                
        except tornado.web.HTTPError:
            raise
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Errore durante la generazione della convenzione: {str(e)}")

class ProcessAllHandler(tornado.web.RequestHandler):
    def get(self):
        process_all_convenzioni()
        self.write("Elaborazione di tutte le convenzioni completata. I file sono stati salvati nella directory 'convenzioni_generate'.")

def make_app():
    return tornado.web.Application([
        (r"/generate", ConvenzioneHandler),
        (r"/process-all", ProcessAllHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("Server Tornado avviato su http://localhost:8888")
    print("Usa /process-all per elaborare tutte le convenzioni")
    print("Usa /generate?convenzione_id=X per una convenzione specifica")
    print("Usa /generate?action=all per elaborare tutte le convenzioni tramite API")
    tornado.ioloop.IOLoop.current().start()