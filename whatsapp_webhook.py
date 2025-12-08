from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from rag_engine import get_ai_response
from news_engine import fetch_outbreak_news

app = Flask(__name__)

@app.route('/whatsapp', methods=['POST'])
def whatsapp():
    """
    Webhook to handle incoming WhatsApp messages via Twilio.
    """
    # Get the message the user sent our Twilio number
    incoming_msg = request.values.get('Body', '').strip()
    sender = request.values.get('From', '')
    
    print(f"Message from {sender}: {incoming_msg}")

    # Fetch real-time news to include in context
    # In a production app, we might cache this to avoid fetching on every message
    current_alert = fetch_outbreak_news()

    # Get response from RAG Engine
    ai_reply = get_ai_response(incoming_msg, news_alert=current_alert)
    print(f"DEBUG - Generated AI Reply: {ai_reply}")

    # Create Twilio Response
    resp = MessagingResponse()
    msg = resp.message()
    msg.body(ai_reply)

    return str(resp), 200, {'Content-Type': 'application/xml'}

@app.route('/', methods=['GET'])
def home():
    return "Swasthya Sathi Webhook is Running! Use /whatsapp for the webhook."

if __name__ == '__main__':
    # INSTRUCTIONS FOR RUNNING WITH NGROK:
    # 1. Run this app: `python whatsapp_webhook.py` (It runs on localhost:5000)
    # 2. Install Ngrok: https://ngrok.com/download
    # 3. Run Ngrok: `ngrok http 5000`
    # 4. Copy the "Forwarding" URL (e.g., https://1234-56-78-90.ngrok-free.app)
    # 5. Go to Twilio Console > Messaging > Try it out > Send a WhatsApp message
    # 6. In "Sandbox Settings", paste the Ngrok URL + "/whatsapp" into the "When a message comes in" field.
    #    Example: https://1234-56-78-90.ngrok-free.app/whatsapp
    # 7. Save and test by sending a message to the Sandbox number.
    
    app.run(debug=True, port=5000)
