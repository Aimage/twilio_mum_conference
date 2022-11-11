import os
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Dial
from twilio.rest import Client

TWILIO_NUMBER = '+17076752295' # twilio number from where you can make an outgoing call
MODERATOR = '+261348009092'  # mum phone number
CONFERENCE_NAME = "Mum_conference"
CHILDREN_NUMBERS = [("Toto", "+261343844002")] # set of label and number for each children


IS_CONFERENCE_START = False

ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')


TWILIO_CLIENT = Client(ACCOUNT_SID, AUTH_TOKEN)

app = Flask(__name__)


@app.route("/voiceconference", methods=['GET', 'POST'])
def call():
    """Return TwiML for a moderated conference call."""
    base_url = request.url_root

    # Start our TwiML response
    response = VoiceResponse()
    print(f"BASE_URl: {base_url}")

    # Start with a <Dial> verb
    with Dial() as dial:
        # If the caller is our MODERATOR, then start the conference when they
        # join and end the conference when they leave
        if request.values.get('From') == MODERATOR:
            dial.conference(
                CONFERENCE_NAME,
                start_conference_on_enter=True,
                end_conference_on_exit=True,
                status_callback=f"{base_url}confstatus",
                status_callback_event='start end join leave mute hold',
                # status_callback_event='start end join leave mute hold',
                # wait_url=f"{base_url}confstatus"
            )
        # else:
        #     # Otherwise have the caller join as a regular participant
        #     dial.conference('My conference', start_conference_on_enter=False)

    response.append(dial)
    return str(response)


def add_participant(number, conference_name, label=""):
    participant = TWILIO_CLIENT.conferences(
        conference_name
    ).participants.create(
        label=label,
        early_media=True,
        beep='onEnter',
        from_=TWILIO_NUMBER,
        to=number)
    return participant


@app.route("/confstatus", methods=['POST', 'GET'])
def status():
    global IS_CONFERENCE_START
    event = request.args.get("StatusCallbackEvent")
    # print(f"event: {event}")
    if event == "participant-join" and IS_CONFERENCE_START is False:
        for child_number in CHILDREN_NUMBERS:
            label, number = child_number
            add_participant(number, CONFERENCE_NAME, label)
    if event == "conference-start":
        IS_CONFERENCE_START = True
    if event == "conference-end":
        IS_CONFERENCE_START = False
    return ""


@app.route("/hello", methods=['GET', 'POST'])
def hello():
    return f"Hello:{request.url_root}"


if __name__ == "__main__":
    app.run(debug=False, port=5000)
