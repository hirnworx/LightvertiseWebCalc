import smtplib
import argparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(company_name, customer_name, customer_email, customer_phone, customer_street, customer_zipcode, customer_city, error_message):
    from_email = "info@lightvertise.de"
    to_email = "info@lightvertise.de"
    subject = "New Contact Form Submission"
    
    # Create the email content
    body = f"""\
    <html>
        <body>
            <p>Company Name: {company_name}<br>
            Customer Name: {customer_name}<br>
            Customer Email: {customer_email}<br>
            Customer Phone: {customer_phone}<br>
            Customer Street: {customer_street}<br>
            Customer Zipcode: {customer_zipcode}<br>
            Customer City: {customer_city}<br>
            Error Message: {error_message}</p>
        </body>
    </html>
    """
    
    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))
    
    try:
        print("Connecting to SMTP server...")
        server = smtplib.SMTP('localhost', 25)  # Use localhost and the default port 25 for unencrypted, unauthenticated SMTP
        print("Sending email...")
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--company_name", required=True)
    parser.add_argument("--customer_name", required=True)
    parser.add_argument("--customer_email", required=True)
    parser.add_argument("--customer_phone", required=True)
    parser.add_argument("--customer_street", required=True)
    parser.add_argument("--customer_zipcode", required=True)
    parser.add_argument("--customer_city", required=True)
    parser.add_argument("--error_message", required=True)
    args = parser.parse_args()

    send_email(
        args.company_name, args.customer_name, args.customer_email, 
        args.customer_phone, args.customer_street, args.customer_zipcode, 
        args.customer_city, args.error_message
    )
