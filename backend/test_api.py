import requests
import os
from dotenv import load_dotenv

load_dotenv()

url = "https://api.sendgrid.com/v3/mail/send"
headers = {
    "Authorization": f"Bearer {os.getenv('SENDGRID_API_KEY')}",
    "Content-Type": "application/json"
}

data = {
    "personalizations": [{"to": [{"email": "shazdataconsult@gmail.com"}]}],
    "from": {"email": "moro.zakaria@saveluguma.gov.gh"},
    "subject": "API Test",
    "content": [{"type": "text/plain", "value": "Hello from SendGrid API!"}]
}

response = requests.post(url, headers=headers, json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")