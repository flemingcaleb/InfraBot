import os				# To access tokens
from InfraBot import DantesUpdater	# To access DantesUpdator
from slackclient import SlackClient
from flask import Flask
from flask import request

app = Flask(__name__)

token = os.environ['TESTING_TOKEN']
sc = SlackClient(token)

@app.route("/")
def main():
    return "Welcome"

@app.route("/test",methods=['POST'])
def test():
    print("RECIEVED TEST!")
    sendMessage("Hello from /test", "#general")
    return "Test Sent, did you see the prompt?"

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
    dante = DantesUpdater.DantesUpdater(os.environ['TESTING_TOKEN'])
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

if __name__ == "__InfraBot__":
    app.run()
