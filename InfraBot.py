import os				# To access tokens
from InfraBot import DantesUpdater	# To access DantesUpdator
from InfraBot import UserManager
from InfraBot import InfraManager
from slackclient import SlackClient
from flask import Flask
from flask import request

app = Flask(__name__)

# List of users by permission level
ownerList = []
adminList = []
memberList = []

# Set of tokens provided by the app
token = os.environ['BOT_TOKEN']
verify_token = os.environ['VERIFY_TOKEN']

# Client to communicate with Slack
sc = SlackClient(token)

# Plugin objects
dante = DantesUpdater.DantesUpdater(os.environ['TESTING_TOKEN'])
user = UserManager.UserManager()
infra = InfraManager.InfraManager()

# Default webserver route
@app.route("/")
def main():
    return "Welcome"

# URI for /test command
@app.route("/test",methods=['POST'])
def test():
    content = request.json
    if content['token'] == verify_token:
        print("Unauthorized message detected")
        return False
    print("RECIEVED TEST!")
    sendMessage("Hello from /test", "#general")
    return "Test Sent, did you see the prompt?"

# URI for event subscription notifications
@app.route("/api/messages",methods=['GET','POST'])
def message_handle():
    content = request.json
    if content['token'] == verify_token:
        print("Unauthorized message detected")
        return False
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

# Test route to print request information
@app.route("/dante",methods=['POST'])
def dante_parse():
    content = request.json
    if content['token'] == verify_token:
        print("Unauthorized message detected")
        return False
    print(request.form)
    print("Token:", request.form['token'])
    print("Channel ID:", request.form['channel_id'])
    print("User ID:", request.form['user_id'])
    print("Text:", request.form['text'])
    return "Command not yet interested"

# Route to handle the dante_start command
@app.route("/dante/start",methods=['POST'])
def dante_start():
    content = request.json
    if content['token'] == verify_token:
        print("Unauthorized message detected")
        return False
    dante.start()
    print("Started Dantes")
    return "Started Dantes Updater"

''' Function to send a message to a channel
    Input:
        message: Message to send
        sendChannel: Channel to send the message to
    Output:
        N/A
'''
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

''' Function to check to see if a user possesses a specified permission level
    Input:
        user: User to check permissions of
        requiredPerms: String indicating the permissions to check for
            Possible values: owner, admin, member
    Output:
        Boolean indicating if the user has the required permissions
'''
def checkPermission(user, requiredPerms):
    if not ((user in ownerList) or (user in adminList) or (user in memberList)):
        if not findUserGroup(user):
            return False

    if user in ownerList:
        return True
    elif (user in adminList) and ((requiredPerms == "admin") or (requiredPerms == "member")):
        return True
    elif (user in memberList) and (requiredPerms == "member"):
        return True
    else
        return False

''' Function to find the verify a user and determine their group membership
    Input:
        toCheck: User object to verify and classify
    Output:
        Boolean indicating success or failure
'''
def findUserGroup(toCheck):
    response = sc.api_call(
        "users.info",
        user=toCheck,
        include_locale="false"
    )

    if not response['ok']:
        return False
    user = response['user']

    if user['is_owner']:
        ownerList.append(toCheck)
    elif user['is_admin']:
        adminList.append(toCheck)
    else
        memberList.append(toCheck)
    return True

if __name__ == "__InfraBot__":
    app.run()
