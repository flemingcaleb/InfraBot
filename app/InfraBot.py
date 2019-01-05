import os				# To access tokens

# Copyright (c) 2015-2016 Slack Technologies, Inc
from slackclient import SlackClient
# Copyright (c) 2015 by Armin Ronacher and contributors. See AUTHORS for more details.
from flask import Flask
from flask import request
from flask import redirect
from flask_sqlalchemy import SQLAlchemy
import Helper

# Copyright (c) 2012-2014 Ivan Akimov, David Aurelio
from hashids import Hashids

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = Helper.getUrl(os.environ['DB_USER'],os.environ['DB_PASS'],os.environ['DB_NAME'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

import DantesUpdater	# To access DantesUpdator
import Updater
import UserManager
import InfraManager
import Database
import AgentManager
import StatusManager

# Set of tokens provided by the app
clientID = os.environ['CLIENT_ID']
clientSecret = os.environ['CLIENT_SECRET']
veritoken = os.environ['VERIFY_TOKEN']
commandSalt = os.environ['COMMAND_SALT']
agentSalt = os.environ['AGENT_SALT']

# Dictionary of SlackClients stored by TeamID
clientDictionary = {}

# Plugin objects
dante = DantesUpdater.Dantes_Updater()
user = UserManager.UserManager()
infra = InfraManager.InfraManager()
update = Updater.Updater()
status = StatusManager.StatusManager()

commandDict = {
        'dante':dante.api_entry,
        'infra':infra.api_entry,
        'user':user.api_entry,
        'update':update.api_entry,
        'agent':AgentManager.api_entry,
        'status':status.api_entry
        }

# Encoder objects
commandHashids = Hashids(salt=commandSalt)
agentHashids = Hashids(salt=agentSalt)

# Default webserver route
@app.route("/")
def main():
    return "Welcome"

# URI for /test command
@app.route("/test",methods=['GET','POST'])
def test():
    content = request.form

    if content['token'] != veritoken:
        print("Unauthorized message detected")
        return 401
    print("RECIEVED TEST!")
    sendMessage("Hello from /test", content['channel_id'], content['team_id'])
    return "Test Sent, did you see the prompt?"

# URI for event subscription notifications
@app.route("/api/messages",methods=['GET','POST'])
def message_handle():
    content = request.json

    if content['token'] != veritoken:
        print("Unauthorized message detected")
        return 401
    if content['type'] == "url_verification":
        print("Received verification message")
        return content['challenge']

    curEvent = content['event']
    team_id = content['team_id']
    
    if curEvent['type'] == 'message':
        if 'text' in curEvent and curEvent['text'].startswith("!"):
            command = curEvent['text'][1:]
            key = command.split(' ', 1)[0]
            if key in commandDict:
                commandDict[key](command[len(key)+1:], curEvent['channel'], curEvent['user'], team_id)
            else:
                print("Command Not Found")
                sendHelp("Command \"" + key + "\"" + " Not Found", curEvent['channel'], curEvent['user'], team_id)
        else:
            print("Message contains no text")
    else:
        print("Event not a message")
        print(content)
    return "200"

@app.route("/api/slash/set_admin_channel",methods=['POST'])
def slash_set_admin_channel():
    channel = request.form['channel_id']
    user = request.form['user_id']
    team_id = request.form['team_id']
    if request.form['token'] != veritoken:
        print("Unauthorized mesage detected")
        return 401

    print("Channel: ", channel)
    if not checkPermission(user, "owner", team_id):
        print(user + " attempted to set admin channel of workspace " + team_id)
        sendEphemeral("Access Denied - Must be Owner to set admin channel", channel, user, team_id)
        return ('', 200)

    curWorkspace = Database.Workspaces.query.filter_by(team_id=team_id).first()
    if curWorkspace is None:
        print("Workspace " + team_id + " not found")
        return 400

    sendEphemeral("Set Admin Channel", channel, user, team_id)
    curWorkspace.admin_channel = channel
    Database.db.session.commit()
    return ('', 200)

# URI for an agent with ID <id> to retrieve a list of unfetched commandIDs
@app.route("/api/agent/<id>/command",methods=['GET'])
def agent_id_command(id):
    return 404

# URI for an agent to get a specific command and post the result
@app.route("/api/agent/<aid>/command/<cid>",methods=['GET', 'POST'])
def agent_id_command_id(aid, cid):
    return 404

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
''' Function to send a message to the designated admin channel
    Input:
        message: Message to send to the admins
        team_id: Team whose admins should be contacted

    Output:
        boolean indicating if the admins have been contacted
'''
def notifyAdmins(message, team_id):
    workspace = Database.Workspaces.query.filter_by(team_id=team_id).first()
    if workspace is None:
        print("Workspace " + team_id + " not found")
        return False

    if workspace.admin_channel is None:
        print("No admin channel defined for workspace " + team_id)
        return False

    sendMessage(message, workspace.admin_channel, team_id)
    return True

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
    elif (curPermissions == Database.permissions.admin) and not (requiredPerms == Database.permissions.owner.name):
        return True
    elif requiredPerms == Database.permissions.user.name:
        return True
    else:
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

def getUserName(user_id, team):
    client,_ = getClient(team)
    if client is None:
        print("Client not found: ", team)
        return ""
    response = client.api_call(
        "users.info",
        user=user_id,
        include_locale="false"
    )
    return response['user']['name']

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

def sendHelp(message, sendChannel, sendUserID, sendTeamID):
    messageString = ""
    if not message is None:
        messageString += message +"\n\n"
    messageString += "InfraBot Help:\n"
    messageString += "\t!help - Prints this help prompt\n"
    messageString += "\t!<module name> help - Prints the help for a given module\n"
    messageString += "\nModule List:"
    for module in commandDict:
        print(module):

    InfraBot.sendEphemeral(messageString, sendChannel, sendUserID, sendTeamID)

if __name__ == '__main__':
    main()
