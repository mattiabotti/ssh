import poplib, smtplib, email
from email.parser import Parser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def receive_emails(email_address, password, start_date, end_date, pop3_server="pop.gmail.com"):
    """Retrieve emails from a POP3 server within a date range."""
    try:
        server = poplib.POP3_SSL(pop3_server, 995)
        server.user(email_address)
        server.pass_(password)
        
        email_count, _ = server.stat()
        emails = []

        for i in range(1, email_count + 1):
            response, lines, _ = server.retr(i)
            message_content = "\n".join(line.decode() for line in lines)
            message = Parser().parsestr(message_content)
            
            email_date = message["Date"]
            try:
                email_datetime = datetime.strptime(email_date, "%a, %d %b %Y %H:%M:%S %z")
            except ValueError:
                continue
            
            if start_date <= email_datetime <= end_date:
                emails.append({
                    "from": message["From"],
                    "subject": message["Subject"],
                    "body": message.get_payload()
                })

        server.quit()
        return emails
    except Exception as e:
        raise RuntimeError(f"Error receiving emails: {e}")

def send_email(email_address, password, to_email, subject, body, smtp_server="smtp.gmail.com", smtp_port=587):
    """Send an email using an SMTP server."""
    try:
        msg = MIMEMultipart()
        msg['From'] = email_address
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_address, password)
        server.sendmail(email_address, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        raise RuntimeError(f"Error sending email: {e}")
