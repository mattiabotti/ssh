import tornado.ioloop
import tornado.web
import requests
import settings
import mail_handler
import sqlite3

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("sito_mail.html")

    def post(self):
        # Legge i dati usando i nomi definiti nel template in minuscolo
        anno_scolastico = self.get_argument("anno_scolastico")
        inizio_primo_periodo = self.get_argument("inizio_primo_periodo")
        fine_primo_periodo = self.get_argument("fine_primo_periodo")
        inizio_secondo_periodo = self.get_argument("inizio_secondo_periodo")
        fine_secondo_periodo = self.get_argument("fine_secondo_periodo")
        link_modulo = self.get_argument("link_modulo")
        prof_1 = self.get_argument("prof_1")
        prof_2 = self.get_argument("prof_2")
        print ("Dati ricevuti")
    
        with open("mail.txt", "r", encoding="utf-8") as file:
            testo = file.read()
        testo = testo.replace("[[ANNO_SCOLASTICO]]", anno_scolastico)
        testo = testo.replace("[[INIZIO_PRIMO_PERIODO]]", inizio_primo_periodo)
        testo = testo.replace("[[FINE_PRIMO_PERIODO]]", fine_primo_periodo)
        testo = testo.replace("[[INIZIO_SECONDO_PERIODO]]", inizio_secondo_periodo)
        testo = testo.replace("[[FINE_SECONDO_PERIODO]]", fine_secondo_periodo)
        testo = testo.replace("[[LINK_MODULO]]", link_modulo)
        testo = testo.replace("[[PROF_1]]", prof_1)
        testo = testo.replace("[[PROF_2]]", prof_2)
        print ("mail modificata")
        self.render("visualizza_mail.html", mail_text=testo)


class SendEmailHandler(tornado.web.RequestHandler):
    def post(self):
        mail_text = self.get_argument("mail_text")
        subject = f"Richiesta disponibilità PCTO"

        try:
            conn = sqlite3.connect("db.sqlite3")
            cursor = conn.cursor()
            cursor.execute("SELECT email_referente FROM aziende")
            results = cursor.fetchall()
        except Exception as e:
            self.write("Errore nella connessione al database: " + str(e))
            return
        finally:
            if conn:
                conn.close()
        
        print(results)

        # Estrae gli indirizzi email dalla query
        emails = [row[0] for row in results if row[0]]
        print(f"Invio della mail a {len(emails)} indirizzi.")

        # Itera su ogni email e invia la mail (la funzione invia_mail è ipotizzata nel modulo mail_handler)
        for email in emails:
            try:
                #send_email(email_address, password, to_email, subject, body, smtp_server="smtp.gmail.com", smtp_port=587)
                mail_handler.send_email("alessandra.mogliazza@fermi.mo.it", settings.GOOGLE_APP_KEY, email, subject, mail_text)
            except Exception as e:
                print(f"Errore nell'invio a {email}: {e}")

        self.render("sito_mail.html")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/send_email", SendEmailHandler)
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("Server running at http://localhost:8888")
    tornado.ioloop.IOLoop.current().start()