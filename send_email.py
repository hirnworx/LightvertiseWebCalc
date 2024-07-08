from flask_mail import Mail, Message
from flask import Flask, request, jsonify

app = Flask(__name__)

# Email configuration
app.config['MAIL_SERVER'] = 'lightvertise.de'  # Replace with your SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'info@lightvertise.de'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'WKCdnPaRHirnworx92@'  # Replace with your email password

mail = Mail(app)

def send_email(company_name, customer_name, customer_email, customer_phone, customer_street, customer_zipcode, customer_city):
    try:
        # Compose email
        msg = Message("Neue Anfrage von " + customer_name,
                      sender=app.config['MAIL_USERNAME'],
                      recipients=["recipient@example.com"])  # Replace with the recipient email
        msg.body = f"""
        Firma: {company_name}
        Name: {customer_name}
        E-mail: {customer_email}
        Telefon: {customer_phone}
        Straße: {customer_street}
        PLZ: {customer_zipcode}
        Stadt: {customer_city}
        """

        mail.send(msg)
        return True

    except Exception as e:
        print(e)
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--company_name', required=True)
    parser.add_argument('--customer_name', required=True)
    parser.add_argument('--customer_email', required=True)
    parser.add_argument('--customer_phone', required=True)
    parser.add_argument('--customer_street', required=True)
    parser.add_argument('--customer_zipcode', required=True)
    parser.add_argument('--customer_city', required=True)

    args = parser.parse_args()

    success = send_email(args.company_name, args.customer_name, args.customer_email, args.customer_phone, args.customer_street, args.customer_zipcode, args.customer_city)
    
    if success:
        print("Email sent successfully!")
    else:
        print("Failed to send email.")