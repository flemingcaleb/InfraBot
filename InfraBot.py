import os				# To access tokens
from InfraBot import DantesUpdater	# To access DantesUpdator
from InfraBot import UserManager
from InfraBot import InfraManager
from slackclient import SlackClient
from flask import Flask
from flask import request

app = Flask(__name__)

token = os.environ['TESTING_TOKEN']
sc = SlackClient(token)

dante = DantesUpdater.DantesUpdater(os.environ['TESTING_TOKEN'])
user = UserManager.UserManager()
infra = InfraManager.InfraManager()

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
            dante.api_entry(curEvent['text'][len("!dante "):], curEvent['channel'], curEvent['user'])
        elif curEvent['text'].startswith("!user "):
            user.api_entry(curEvent['text'][len("!user "):], curEvent['channel'], curEvent['user'])
        elif curEvent['text'].startswith("!infra "):
            infra.api_entry(curEvent['text'][len("!infra "):], curEvent['channel'], curEvent['user'])
        #else:
        #    sendEphemeral("Command not found", curEvent['channel'], curEvent['user'])
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
        text=message
        )

if __name__ == "__InfraBot__":
    app.run()
