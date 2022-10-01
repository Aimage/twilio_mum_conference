import os
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Dial
from twilio.rest import Client

app = Flask(__name__)

MODERATOR = 'xxxxxxxxx'  # mum phone number
CONFERENCE_NAME = "Mum_conference"
CHILDREN_NUMBERS = [""]

ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')


@app.route("/voiceconference", methods=['GET', 'POST'])
def call():
    """Return TwiML for a moderated conference call."""
    base_url = request.url_root

    # Start our TwiML response
    response = VoiceResponse()

    # Start with a <Dial> verb
    with Dial() as dial:
        # If the caller is our MODERATOR, then start the conference when they
        # join and end the conference when they leave
        if request.values.get('From') == MODERATOR:
            dial.conference(CONFERENCE_NAME,
                            start_conference_on_enter=True,
                            end_conference_on_exit=True,
                            status_callback=f"{base_url}/confstatus")
        else:
            # Otherwise have the caller join as a regular participant
            dial.conference('My conference', start_conference_on_enter=False)

    response.append(dial)
    return str(response)


def add_participant(number, conference_name):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    participant = client.conferences(conference_name).participants.create(
        label='customer',
        early_media=True,
        beep='onEnter',
        status_callback='https://myapp.com/events',
        status_callback_event=['ringing'],
        record=True,
        # from_='+15017122661',
        to=number)
    return participant


@app.route("/confstatus", methods=['POST'])
def status():
    event = request.args.get("StatusCallbackEvent")
    if event == "conference-start":
        for number in CHILDREN_NUMBERS:
            add_participant(number, CONFERENCE_NAME)
    return


@app.route("/hello", methods=['GET', 'POST'])
def hello():
    return f"Hello:{request.url_root}"


if __name__ == "__main__":
    app.run(debug=True, port=5000)
