import requests
import json

BACKEND_URL = "http://localhost:8000/send_mail"
API_KEY = "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"

def extract_mail_json(user_input: str):
    url = "https://openrouter.ai/api/v1/chat/completions"
    
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
                    "and sender name is bharath, position is AI Developer and Contact Information +91 9487127290 ."
                    " Always return valid JSON only, no extra text."
                )
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
        "response_format": { "type": "json_object" }  
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    
    return json.loads(content)

def normalize_emails(emails):

    normalized = []
    for email in emails:
        email = email.strip()
        if "@" not in email:
            email += "@zohocorp.com"
        normalized.append(email)
    return normalized


user_input = input("Enter your mail request: ")

mail_json = extract_mail_json(user_input)

mail_json["to"] = normalize_emails(mail_json.get("to", []))
mail_json["cc"] = normalize_emails(mail_json.get("cc", [])) if mail_json.get("cc") else []


response = requests.post(BACKEND_URL, json=mail_json)

print("📨 Response:", response.json())