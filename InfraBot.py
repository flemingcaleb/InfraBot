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
    return "OK"

@app.route("/dante/start",methods=['POST'])
def dante_start():
    dante = DantesUpdater.DantesUpdater(os.environ['TESTING_TOKEN'])
    dante.start()
    print("Started Dantes")
    return "OK"
#dante = danteUpdater(os.environ['TESTING_TOKEN'])

#dante.start()

#input()

#dante.stop()
#print("Waiting for thread to stop")
#dante.join()

def sendMessage (message, sendChannel):
    print("Sending Message")
    sc.api_call(
        "chat.postMessage",
        channel=sendChannel,
        text=message
        )

if __name__ == "__InfraBot__":
    app.run()
