from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Dial

app = Flask(__name__)

MODERATOR = 'xxxxxxxxx' # mum phone number
CONFERENCE_NAME = "Mum_conference"
BASE_URL = "http://my_url_ngrok_url"


@app.route("/voiceconference", methods=['GET', 'POST'])
def call():
    """Return TwiML for a moderated conference call."""
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
                            status_callback=f"{BASE_URL}/confstatus")
        else:
            # Otherwise have the caller join as a regular participant
            dial.conference('My conference', start_conference_on_enter=False)

    response.append(dial)
    return str(response)

@app.route("/hello", methods=['GET', 'POST'])
def hello():
    return "Hello"

if __name__ == "__main__":
    app.run(debug=True)
