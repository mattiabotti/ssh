import sqlite3
import csv
import os

def init_db(csv_path=None):
    """
    Initialize the database and optionally import students from a CSV file.
    
    :param csv_path: Optional path to a CSV file containing student data
    """
    # Connect to the database
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()

    # Creazione tabella studenti con nuovo campo classe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS studenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            classe TEXT
        )
    ''')

    # Creazione tabella aziende
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aziende (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            via TEXT,
            cap TEXT,
            comune TEXT,
            nome_referente TEXT,
            email_referente TEXT,
            cellulare_referente TEXT,
            disponibilita_lavoro_estivo BOOLEAN DEFAULT 0,
            osservazioni TEXT
        )
    ''')

    # Creazione tabella associazioni studenti-aziende con il periodo
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS associazioni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_studente INTEGER NOT NULL,
            id_azienda INTEGER NOT NULL,
            data_inizio DATE,
            data_fine DATE,
            FOREIGN KEY (id_studente) REFERENCES studenti(id),
            FOREIGN KEY (id_azienda) REFERENCES aziende(id)
        )
    ''')

    # Inserimento dati di esempio per studenti se non viene fornito un CSV
    if not csv_path or not os.path.exists(csv_path):
        studenti = [
            ('Mario Rossi', 'mario@example.com', '4A'),
            ('Luca Bianchi', 'luca@example.com', '4B')
        ]
        cursor.executemany("INSERT OR IGNORE INTO studenti (nome, email, classe) VALUES (?, ?, ?)", studenti)
    else:
        # Importa studenti dal file CSV
        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                # Usa csv.reader per leggere il file
                csv_reader = csv.reader(csvfile)
                
                # Salta l'intestazione se presente
                header = next(csv_reader, None)
                
                # Prepara gli studenti dal CSV
                studenti = []
                for row in csv_reader:
                    # Verifica se il CSV contiene la colonna classe
                    if len(row) >= 3:
                        nome = row[0].strip()
                        email = row[1].strip()
                        classe = row[2].strip()
                        
                        # Validazione base
                        if nome and email:
                            studenti.append((nome, email, classe))
                    elif len(row) >= 2:
                        nome = row[0].strip()
                        email = row[1].strip()
                        
                        # Se non c'è la classe, usiamo NULL
                        if nome and email:
                            studenti.append((nome, email, None))
                
                # Inserisci gli studenti nel database
                if studenti:
                    cursor.executemany("INSERT OR IGNORE INTO studenti (nome, email, classe) VALUES (?, ?, ?)", studenti)
                    print(f"Importati {len(studenti)} studenti dal file CSV.")
                else:
                    print("Nessuno studente trovato nel file CSV.")
        
        except FileNotFoundError:
            print(f"Errore: File CSV non trovato in {csv_path}")
        except csv.Error as e:
            print(f"Errore durante la lettura del file CSV: {e}")
        except Exception as e:
            print(f"Si è verificato un errore imprevisto: {e}")

    # Inserimento dati di esempio per aziende
    aziende = [
        ('TechCorp', 'Via Roma 123', '20100', 'Milano', 'Giovanni Verdi', 'mattia.botti@fermi.mo.it', '3331234567', 1, 'Disponibili per stage estivi in ambito sviluppo software'),
        ('MediCare', 'Via Salute 45', '00192', 'Roma', 'Laura Bianchi', 'alessio.marchetti@fermi.mo.it', '3479876543', 0, "Preferenza per tirocini durante l'anno scolastico")
    ]
    cursor.executemany("INSERT OR IGNORE INTO aziende (nome, via, cap, comune, nome_referente, email_referente, cellulare_referente, disponibilita_lavoro_estivo, osservazioni) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", aziende)

    # Inserimento associazioni con periodo (date di inizio e fine)
    associazioni = [
        (1, 1, '2025-06-15', '2025-07-15'),
        (2, 2, '2025-09-01', '2025-10-15')
    ]
    cursor.executemany("INSERT OR IGNORE INTO associazioni (id_studente, id_azienda, data_inizio, data_fine) VALUES (?, ?, ?, ?)", associazioni)

    conn.commit()
    conn.close()

def create_sample_csv(filename='studenti.csv'):
    """
    Crea un file CSV di esempio per l'importazione degli studenti.
    
    :param filename: Nome del file CSV da creare
    """
    sample_data = [
        ['Nome', 'Email', 'Classe'],  # Intestazione aggiornata
        ['Giovanni Rossi', 'giovanni.rossi@example.com', '4A'],
        ['Anna Bianchi', 'anna.bianchi@example.com', '4B'],
   
    ]
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerows(sample_data)
        print(f"File CSV di esempio {filename} creato con successo.")
    except Exception as e:
        print(f"Errore durante la creazione del file CSV: {e}")

if __name__ == "__main__":
    # Crea un file CSV di esempio
    create_sample_csv()
    
    # Inizializza il database con il CSV di esempio
    init_db('studenti.csv')
    
    print("Database aggiornato e popolato con dati di esempio completi.")