from flask import Flask, request, jsonify, redirect
import os
import pickle
import base64
import json
import requests
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
from flask_cors import CORS  

app = Flask(__name__)
CORS(app)  

CLIENT_SECRETS_FILE = "credentials.json"
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CREDENTIALS = None

API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


@app.route("/")
def home():
    return "📧 Gmail AI Agent Backend Running"

@app.route("/login")
def login():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri="http://localhost:8000/callback"
    )
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    return redirect(auth_url)

@app.route("/callback")
def callback():
    global CREDENTIALS
    code = request.args.get("code")
    if not code:
        return "No code received", 400

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri="http://localhost:8000/callback"
    )
    flow.fetch_token(code=code)
    CREDENTIALS = flow.credentials

    with open("token.pkl", "wb") as f:
        pickle.dump(CREDENTIALS, f)

    return jsonify({"message": "Login successful!"})


def normalize_emails(emails):
    normalized = []
    for email in emails:
        email = email.strip()
        if "@" not in email:
            email += "@zohocorp.com"
        normalized.append(email.lower())
    return normalized

def extract_mail_json(user_input: str):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "x-ai/grok-4-fast:free",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an email parser. From user input, extract: "
                    "{ \"to\": [string], \"cc\": [string] or [], \"subject\": string, \"body\": string }. "
                    "Sender name is Bharath, Position is AI Developer, Contact Information +91 9487127290. "
                    "Always return valid JSON only, no extra text."
                )
            },
            {"role": "user", "content": user_input}
        ],
        "response_format": {"type": "json_object"}
    }

    response = requests.post(OPENROUTER_URL, headers=headers, data=json.dumps(payload))
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    return json.loads(content)


@app.route("/send_ai_mail", methods=["POST"])
def send_ai_mail():
    global CREDENTIALS
    if not CREDENTIALS:
        if os.path.exists("token.pkl"):
            with open("token.pkl", "rb") as f:
                CREDENTIALS = pickle.load(f)
        else:
            return jsonify({"error": "Please login first at /login"}), 401

    if CREDENTIALS.expired and CREDENTIALS.refresh_token:
        CREDENTIALS.refresh(Request())

    service = build('gmail', 'v1', credentials=CREDENTIALS)

    data = request.json
    user_input = data.get("input")
    if not user_input:
        return jsonify({"error": "Missing 'input' in request"}), 400

    mail_json = extract_mail_json(user_input)

    mail_json["to"] = normalize_emails(mail_json.get("to", []))
    mail_json["cc"] = normalize_emails(mail_json.get("cc", [])) if mail_json.get("cc") else []

    message = MIMEText(mail_json["body"])
    message['to'] = ", ".join(mail_json["to"])

    if mail_json["cc"]:
        message['cc'] = ", ".join(mail_json["cc"])
    message['subject'] = mail_json["subject"]

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    sent_message = service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()

    return jsonify({
        "message": "Email sent successfully!",
        "id": sent_message['id'],
        "to": mail_json["to"],
        "cc": mail_json["cc"],
        "subject": mail_json["subject"]
    })


if __name__ == "__main__":
    app.run(port=8000, debug=True)
