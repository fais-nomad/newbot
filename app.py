from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

VERIFY_TOKEN = "nomadller_token"
ACCESS_TOKEN = "EAAIvcD0SvAgBOyZBMZBOjOINaeLnPJylNnnczGKno0CG7xfDCEzygfDGcWZBcZCsqv99AMjSiY97NvSI8wfTHXpROGdm6IKz6cCNoQu858mTXzQJWmzq5cM48y4N4CpM4p1unRyHzaJuGZAJjRZCLRiyXZBWv4fVK2IZA8JGm6M7O9JnI7KEhXHhDa43neHj"
PHONE_NUMBER_ID = "680192251841893"

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

CONTACT_NUMBER = "917902663277"  # Faiz's WhatsApp number

PDF_LINKS = {
    "everest_base_camp": "https://drive.google.com/file/d/1SvSSBlG6mtQHbTKIusmi1G3JoTy-YQlV/view?usp=sharing",
    "annapurna_base_camp": "https://drive.google.com/file/d/1SvSSBlG6mtQHbTKIusmi1G3JoTy-YQlV/view?usp=sharing",
    "annapurna_circuit": "https://drive.google.com/file/d/1SvSSBlG6mtQHbTKIusmi1G3JoTy-YQlV/view?usp=sharing",
    "bali": "https://drive.google.com/file/d/1SvSSBlG6mtQHbTKIusmi1G3JoTy-YQlV/view?usp=sharing",
    "manali": "https://drive.google.com/file/d/1SvSSBlG6mtQHbTKIusmi1G3JoTy-YQlV/view?usp=sharing",
    "kashmir": "https://drive.google.com/file/d/1SvSSBlG6mtQHbTKIusmi1G3JoTy-YQlV/view?usp=sharing",
    "friendship_peak": "https://drive.google.com/file/d/1SvSSBlG6mtQHbTKIusmi1G3JoTy-YQlV/view?usp=sharing",
    "yunam_peak": "https://drive.google.com/file/d/1SvSSBlG6mtQHbTKIusmi1G3JoTy-YQlV/view?usp=sharing",
    "mount_nun": "https://drive.google.com/file/d/1SvSSBlG6mtQHbTKIusmi1G3JoTy-YQlV/view?usp=sharing"
}

user_states = {}
user_names = {}

def send_message(phone_id, recipient_id, message):
    url = f"https://graph.facebook.com/v17.0/{phone_id}/messages"
    data = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "text": {"body": message}
    }
    response = requests.post(url, headers=HEADERS, json=data)
    print("send_message response:", response.status_code, response.text)
    return response

def send_buttons(phone_id, recipient_id, text, buttons):
    url = f"https://graph.facebook.com/v17.0/{phone_id}/messages"
    data = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": text},
            "action": {"buttons": buttons[:3]}  # WhatsApp supports max 3 buttons
        }
    }
    response = requests.post(url, headers=HEADERS, json=data)
    print("send_buttons response:", response.status_code, response.text)
    return response

def send_notification_to_contact(user_name, user_phone):
    message_text = f"New user contacted the bot:\nName: {user_name}\nPhone: {user_phone}"
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    data = {
        "messaging_product": "whatsapp",
        "to": CONTACT_NUMBER,
        "text": {"body": message_text}
    }
    response = requests.post(url, headers=HEADERS, json=data)
    print("send_notification_to_contact response:", response.status_code, response.text)
    return response

def welcome_buttons():
    return [
        {"type": "reply", "reply": {"id": "trips", "title": "Trips"}},
        {"type": "reply", "reply": {"id": "treks", "title": "Treks"}},
        {"type": "reply", "reply": {"id": "expeditions", "title": "Expeditions"}}
    ]

def treks_buttons():
    return [
        {"type": "reply", "reply": {"id": "everest_base_camp", "title": "Everest Base Camp"}},
        {"type": "reply", "reply": {"id": "annapurna_base_camp", "title": "Annapurna Base Camp"}},
        {"type": "reply", "reply": {"id": "annapurna_circuit", "title": "Annapurna Circuit"}}
    ]

def trips_buttons():
    return [
        {"type": "reply", "reply": {"id": "bali", "title": "Bali"}},
        {"type": "reply", "reply": {"id": "manali", "title": "Manali"}},
        {"type": "reply", "reply": {"id": "kashmir", "title": "Kashmir"}}
    ]

def expeditions_buttons():
    return [
        {"type": "reply", "reply": {"id": "friendship_peak", "title": "Friendship Peak"}},
        {"type": "reply", "reply": {"id": "yunam_peak", "title": "Yunam Peak"}},
        {"type": "reply", "reply": {"id": "mount_nun", "title": "Mount Nun"}}
    ]

def contact_buttons():
    return [
        {"type": "reply", "reply": {"id": "adhil", "title": "Adhil"}},
        {"type": "reply", "reply": {"id": "faiz", "title": "Faiz"}},
        {"type": "reply", "reply": {"id": "dhanish", "title": "Dhanish"}}
    ]

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification token mismatch", 403

    elif request.method == 'POST':
        data = request.get_json()
        print("Received webhook data:", json.dumps(data))

        if data.get('object') == 'whatsapp_business_account':
            entry = data.get('entry', [])[0]
            changes = entry.get('changes', [])[0]
            value = changes.get('value', {})
            messages = value.get('messages')

            if messages:
                message = messages[0]
                phone_id = value.get('metadata', {}).get('phone_number_id')
                sender_id = message.get('from')
                message_type = message.get('type')

                # First-time user
                if sender_id not in user_states:
                    user_states[sender_id] = 'awaiting_name'
                    send_message(phone_id, sender_id, "Hi! Welcome to Nomadller 👋\nWhat’s your name?")
                    return "OK", 200

                if user_states[sender_id] == 'awaiting_name':
                    if message_type == 'text':
                        user_name = message.get('text', {}).get('body', '').strip()
                        user_names[sender_id] = user_name
                        user_states[sender_id] = 'ready'

                        send_message(phone_id, sender_id, f"Nice to meet you, {user_name}!")
                        send_buttons(phone_id, sender_id, "Choose an option:", welcome_buttons())
                        send_buttons(phone_id, sender_id, "Or chat with an expert:", contact_buttons())
                        send_message(phone_id, sender_id, f"📞 Contact: {CONTACT_NUMBER}")

                        send_notification_to_contact(user_name, sender_id)
                    else:
                        send_message(phone_id, sender_id, "Please enter your name in text.")
                    return "OK", 200

                if user_states[sender_id] == 'ready':
                    if message_type == 'interactive':
                        interactive = message.get('interactive', {})
                        button_id = interactive.get('button_reply', {}).get('id', '')

                        if button_id == 'trips':
                            send_buttons(phone_id, sender_id, "Choose your Trip:", trips_buttons())
                        elif button_id == 'treks':
                            send_buttons(phone_id, sender_id, "Choose your Trek:", treks_buttons())
                        elif button_id == 'expeditions':
                            send_buttons(phone_id, sender_id, "Choose your Expedition:", expeditions_buttons())

                        elif button_id in PDF_LINKS:
                            pdf_url = PDF_LINKS[button_id]
                            send_message(phone_id, sender_id, f"Here is your itinerary: {pdf_url}")
                            send_message(phone_id, sender_id, f"Talk with Expert: {CONTACT_NUMBER}")
                            send_buttons(phone_id, sender_id, "Want to connect with someone?", contact_buttons())

                        elif button_id == "adhil":
                            send_message(phone_id, sender_id, "Chat with Adhil: https://wa.me/918129263766")
                        elif button_id == "faiz":
                            send_message(phone_id, sender_id, "Chat with Faiz (Treks Expert): https://wa.me/917902663277")
                        elif button_id == "dhanish":
                            send_message(phone_id, sender_id, "Chat with Dhanish (Trips): https://wa.me/918129163766")
                        else:
                            send_message(phone_id, sender_id, "Sorry, I didn’t understand. Please choose again.")
                    else:
                        send_buttons(phone_id, sender_id, "Please choose from the options:", welcome_buttons())
                        send_buttons(phone_id, sender_id, "Or chat with an expert:", contact_buttons())

        return "OK", 200

if __name__ == '__main__':
    app.run(port=5050, debug=True)