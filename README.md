# 📧 AI-Powered Gmail Automation Agent

This project is an **AI-driven mail automation system** built using **Flask, OpenRouter (Grok), and Google Gmail API**.  
It allows users to type **any natural language prompt**, and the agent will:

✔️ Understand the intent  
✔️ Extract **To / CC / Subject / Body**  
✔️ Auto-format and structure the email  
✔️ Send it instantly through Gmail  

All with a **single prompt**.

---

## 🚀 Features

### 🔹 1. Prompt-Based Email Generation  
The system uses **Grok-4-Fast (OpenRouter)** to convert natural language into a strict JSON email format containing:

{
  "to": [...],
  "cc": [...],
  "subject": "",
  "body": ""
}
### 🔹 2. Automatic Email Normalization
If a recipient does not contain "@", the agent auto-converts it to:
@zohocorp.com
Converts all emails to lowercase
Removes unwanted whitespace
### 🔹 3. Gmail OAuth Login
A secure login flow using:
credentials.json
OAuth2
Token persistence using token.pkl
### 🔹 4. Fully Automated Email Sending

### 🧠 Architecture Flow
User enters a prompt
Backend sends the prompt to OpenRouter Grok model
Grok returns structured JSON
Email addresses are normalized
Email is built using MIMEText
Gmail API sends the message
Response includes:
message ID
final recipients
subject
