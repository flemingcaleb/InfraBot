import os				# To access tokens

# Copyright (c) 2015-2016 Slack Technologies, Inc
from slackclient import SlackClient
# Copyright (c) 2015 by Armin Ronacher and contributors. See AUTHORS for more details.
from flask import Flask
from flask import request
from flask import redirect
from flask_sqlalchemy import SQLAlchemy
from app import Helper

# Copyright (c) 2012-2014 Ivan Akimov, David Aurelio
from hashids import Hashids

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = Helper.getUrl(os.environ['DB_USER'],os.environ['DB_PASS'],os.environ['DB_NAME'])
db = SQLAlchemy(app)

from app import DantesUpdater	# To access DantesUpdator
from app import Updater
from app import UserManager
from app import InfraManager
from app import Database
from app import AgentManager

# Set of tokens provided by the app
clientID = os.environ['CLIENT_ID']
clientSecret = os.environ['CLIENT_SECRET']
veritoken = os.environ['VERIFY_TOKEN']
commandSalt = os.environ['COMMAND_SALT']
agentSalt = os.environ['AGENT_SALT']

# Dictionary of SlackClients stored by TeamID
clientDictionary = {}

# Plugin objects
dante = DantesUpdater.DantesUpdater()
user = UserManager.UserManager()
infra = InfraManager.InfraManager()
update = Updater.Updater()

commandDict = {
        'dante':dante.api_entry,
        'infra':infra.api_entry,
        'user':user.api_entry,
        'update':update.api_entry,
        'agent':AgentManager.api_entry
        }

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

    if content['token'] == veritoken:
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

    if content['token'] == veritoken:
        print("Unauthorized message detected")
        return False
    if content['type'] == "url_verification":
        print("Received verification message")
        return content['challenge']

    curEvent = content['event']

    if curEvent['type'] == 'message':
        if curEvent['text'].startswith("!"):
            command = curEvent['text'][1:]
            key = command.split(' ', 1)[0]
            if key in commandDict:
                commandDict[key](command[len(key):], curEvent['channel'], curEvent['user'], team_id)
            else:
                print("Command Not Found")
                sendEphemeral("Command Not Found", curEvent['channel'], curEvent['user'], team_id)
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
    if content['token'] == veritoken:
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
    if content['token'] == veritoken:
        print("Unauthorized message detected")
        return False
    dante.start()
    print("Started Dantes")
    return "Started Dantes Updater"

@app.route("/install",methods=['GET'])
def install():
    print("Install reached")
    return redirect("https://slack.com/oauth/authorize?scope=commands,bot,channels:read,groups:read,im:read,mpim:read&client_id=344786415526.344950175959&redirect_url=slack.flemingcaleb.com:5000/install/confirm")

@app.route("/install/confirm", methods=['GET'])
def install_confirm():
    auth = request.args.get('code')
    status = request.args.get('status')
    error = request.args.get('error')

    if error != None:
        return "You have denied access"

    sc = SlackClient("")

    print("Requesting tokens")

    response = sc.api_call(
        "oauth.access",
        client_id=clientID,
        client_secret=clientSecret,
        code=auth
    )

    print(response)

    addClient(response['bot']['bot_access_token'],response['access_token'],veritoken, response['team_id'])
    return "Ok"

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
        curPermissions = addUser(user, team_id)
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
def addUser(toCheck, team):
    print("Adding user")
    client,_ = getClient(team)
    if client is None:
        print("Client not found: ", team)

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

    dbWorkspace = Database.Workspaces.query.filter_by(team_id = team).first()

    newUser = Database.Users(newPerms, dbWorkspace.id, toCheck)
    db.session.add(newUser)
    db.session.commit()

    return newPerms

def getClient(toCheck):
    if not toCheck in clientDictionary:
        #Check for workspace in DB
        dbWorkspace = Database.Workspaces.query.filter_by(team_id = toCheck).first()
        if dbWorkspace is None:
            print("Workspace not found in database")
            return None
        else:
            #Open a SlackClient
            newClient = SlackClient(dbWorkspace.bot_token)
            clientDictionary[toCheck] = newClient, dbWorkspace.verify_token
            return newClient, dbWorkspace.verify_token
    else:
        return clientDictionary[toCheck]

def addClient(bot, access, verify, team):
    newClient = Database.Workspaces(bot, access, veritoken, team)
    db.session.add(newClient)
    db.session.commit()

if __name__ == '__main__':
    main()
