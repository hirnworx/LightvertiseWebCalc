import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email(company_name, customer_name, customer_email, customer_phone, customer_street, customer_zipcode, customer_city):
    message = Mail(
        from_email='info@hirnworx.de',
        to_emails='info@lightvertise.de',
        subject='New Customer Data',
        html_content=f"""
        <p>Company Name: {company_name}</p>
        <p>Customer Name: {customer_name}</p>
        <p>Customer Email: {customer_email}</p>
        <p>Customer Phone: {customer_phone}</p>
        <p>Customer Street: {customer_street}</p>
        <p>Customer Zipcode: {customer_zipcode}</p>
        <p>Customer City: {customer_city}</p>
        """
    )
    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(str(e))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--company_name", required=True)
    parser.add_argument("--customer_name", required=True)
    parser.add_argument("--customer_email", required=True)
    parser.add_argument("--customer_phone", required=True)
    parser.add_argument("--customer_street", required=True)
    parser.add_argument("--customer_zipcode", required=True)
    parser.add_argument("--customer_city", required=True)

    args = parser.parse_args()

    send_email(
        args.company_name,
        args.customer_name,
        args.customer_email,
        args.customer_phone,
        args.customer_street,
        args.customer_zipcode,
        args.customer_city
    )

