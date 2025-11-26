# send_email.py
import requests
from auth_delegated import get_access_token

GRAPH = "https://graph.microsoft.com/v1.0"

def send_report(to_email, subject, body):
    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    email_data = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": body
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": to_email
                    }
                }
            ]
        }
    }

    response = requests.post(
        f"{GRAPH}/me/sendMail",
        headers=headers,
        json=email_data
    )

    if response.status_code == 202:
        print("Email sent successfully!")
    else:
        print("Error sending email:", response.text)
