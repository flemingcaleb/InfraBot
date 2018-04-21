import os				# To access tokens
from InfraBot import DantesUpdater	# To access DantesUpdator
from slackclient import SlackClient
from flask import Flask
from flask import request

app = Flask(__name__)

token = os.environ['TESTING_TOKEN']
sc = SlackClient(token)

dante = DantesUpdater.DantesUpdater(os.environ['TESTING_TOKEN'])

@app.route("/")
def main():
    return "Welcome"

@app.route("/test",methods=['POST'])
def test():
    print("RECIEVED TEST!")
    sendMessage("Hello from /test", "#general")
    return "Test Sent, did you see the prompt?"

@app.route("/api/messages",methods=['GET','POST'])
def message_handle():
    content = request.json
    if content['type'] == "url_verification":
        print("Received verification message")
        return content['challenge']

    curEvent = content['event']

    if curEvent['type'] == 'message':
        if curEvent['text'].startswith("!dante "):
            return dante.api_entry(curEvent['text'][len("!dante "):], curEvent['channel'], curEvent['user_id'])
    else:
        print("Event not a message")
        print(content)
    return "OK"

@app.route("/dante",methods=['POST'])
def dante_parse():
    print(request.form)
    print("Token:", request.form['token'])
    print("Channel ID:", request.form['channel_id'])
    print("User ID:", request.form['user_id'])
    print("Text:", request.form['text'])
    return "Command not yet interested"

@app.route("/dante/start",methods=['POST'])
def dante_start():
    dante.start()
    print("Started Dantes")
    return "Started Dantes Updater"

def sendMessage (message, sendChannel):
    print("Sending Message")
    sc.api_call(
        "chat.postMessage",
        channel=sendChannel,
        text=message
        )

def sendEphemeral (message, sendChannel, sendUserID):
    sc.api_call(
        "chat.postEphemeral",
        channel=sendChannel,
        user=sendUserID,
        as_user=true,
        text=message
        )

if __name__ == "__InfraBot__":
    app.run()
