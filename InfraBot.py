import os				# To access tokens

# Copyright (c) 2015-2016 Slack Technologies, Inc
from slackclient import SlackClient
# Copyright (c) 2015 by Armin Ronacher and contributors. See AUTHORS for more details.
from flask import Flask
from flask import request
from flask_sqlalchemy import SQLAlchemy
from InfraBot import Helper

# Copyright (c) 2012-2014 Ivan Akimov, David Aurelio
from hashids import Hashids

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = Helper.getUrl(os.environ['DB_USER'],os.environ['DB_PASS'],os.environ['DB_NAME'])
db = SQLAlchemy(app)

from InfraBot import DantesUpdater	# To access DantesUpdator
from InfraBot import UserManager
from InfraBot import InfraManager
from InfraBot import Database

# Set of tokens provided by the app
token = os.environ['BOT_TOKEN']
veritoken = os.environ['VERIFY_TOKEN']
commandSalt = os.environ['COMMAND_SALT']
agentSalt = os.environ['AGENT_SALT']

# Client to communicate with Slack
sc = SlackClient(token)

# Dictionary of SlackClients stored by TeamID
clientDictionary['TA4P4C7FG'] = sc, veritoken

# Plugin objects
dante = DantesUpdater.DantesUpdater()
user = UserManager.UserManager()
infra = InfraManager.InfraManager()

# Encoder objects
commandHashids = Hashids(salt=commandSalt)
agentHashids = Hashids(salt=agentSalt)

# Default webserver route
@app.route("/")
def main():
    return "Welcome"

# URI for /test command
@app.route("/test",methods=['POST'])
def test():
    content = request.json
    _,verify_token = getClient(content['team_id'])

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
    team_id = content['team_id']
    _,verify_token = getClient(content['team_id'])

    if content['token'] == verify_token:
        print("Unauthorized message detected")
        return False
    if content['type'] == "url_verification":
        print("Received verification message")
        return content['challenge']

    curEvent = content['event']

    if curEvent['type'] == 'message':
        if curEvent['text'].startswith("!dante "):
            dante.api_entry(curEvent['text'][len("!dante "):], curEvent['channel'], curEvent['user'], team_id)
        elif curEvent['text'].startswith("!user "):
            user.api_entry(curEvent['text'][len("!user "):], curEvent['channel'], curEvent['user'], team_id)
        elif curEvent['text'].startswith("!infra "):
            infra.api_entry(curEvent['text'][len("!infra "):], curEvent['channel'], curEvent['user'], team_id)
        #else:
        #    sendEphemeral("Command not found", curEvent['channel'], curEvent['user'])
    else:
        print("Event not a message")
        print(content)
    return "OK"

# URI for an agent with ID <id> to retrieve a list of unfetched commandIDs
@app.route("/api/agent/<id>/command",methods=['GET'])
def agent_id_command(id):
    return 404

# URI for an agent to get a specific command and post the result
@app.route("/api/agent/<aid>/command/<cid>",methods=['GET', 'POST'])
def agent_id_command_id(aid, cid):
    return 404

# Test route to print request information
@app.route("/dante",methods=['POST'])
def dante_parse():
    content = request.json
    _,verify_token = getClient(content['team_id'])
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
    _,verify_token = getClient(content['team_id'])
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
def sendMessage (message, sendChannel, team_id):
    client,_ = getClient(team_id)
    if client is None:
        print("Team not found: ", team_id)

    client.api_call(
        "chat.postMessage",
        channel=sendChannel,
        text=message
        )

''' Function to send an ephemeral message
    Input:
        message: Message to send
        sendChannel: Channel to send the message in
        sendUserID: User to send the message to
    Output:
        N/A
'''
def sendEphemeral (message, sendChannel, sendUserID, team_id):
    client,_ = getClient(team_id)

    if client is None:
        print("Team not found: ", team_id)
        return

    client.api_call(
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
def checkPermission(user, requiredPerms, team_id):
    dbUser = Database.Users.query.filter_by(user_id = user).first()
    if dbUser is None:
        # Add user to the database
        curPermissions,_ = addUser(user, team_id)
    else:
        curPermissions = dbUser.permission_level

    if curPermissions == Database.permissions.owner:
        print("User owner");
        return True
    elif (curPermissions == Database.permissions.admin) and not (requiredPerms == Database.permissions.owner):
        return True
    elif requiredPerms == Database.permissions.user:
        return True
    else:
        print(curPermissions)
        return False

''' Function to find the verify a user and determine their group membership
    Input:
        toCheck: User object to verify and classify
    Output:
        Boolean indicating success or failure
'''
def addUser(toCheck, team_id):
    print("Adding user")
    client,_ = getClient(team_id)
    if client is None:
        print("Client not found: ", team_id)

    response = client.api_call(
        "users.info",
        user=toCheck,
        include_locale="false"
    )

    if not response['ok']:
        return None
    user = response['user']

    if user['is_owner']:
        # add owner permissions
        newPerms = Database.permissions.owner
    elif user['is_admin']:
        #add admin permissions
        newPerms = Database.permissions.admin
    else:
        #add user permissions
        newPerms =  Database.permissions.user

    newUser = Database.Users(newPerms, 2, toCheck)
    db.session.add(newUser)
    db.session.commit()

    return newPerms

def getClient(team_id):
    if not team_id in clientDictionary:
        return None
    else:
        return clientDictionary[team_id]

if __name__ == '__main__':
    main()
