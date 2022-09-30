from flask import Flask
import os
from twilio.rest import Client

app = Flask(__name__)

CONFERENCE_NAME = "Mum_conference"
CHILDREN_NUMBERS = [""]

ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']


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


if __name__ == "__main__":
    app.run(debug=True)
