import os				# To access tokens

# Copyright (c) 2015-2016 Slack Technologies, Inc
from slackclient import SlackClient
# Copyright (c) 2015 by Armin Ronacher and contributors. See AUTHORS for more details.
from flask import Flask
from flask import request, make_response, Response
from flask import redirect
from flask_sqlalchemy import SQLAlchemy
import json
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
import LabManager

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
lab = LabManager.LabManager()

commandDict = {
        'dante':dante,
        'infra':infra,
        'user':user,
        'update':update,
        'agent':AgentManager,
        'status':status,
        'lab':lab
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

    message_attachments = [
        {
            "fallback": "Upgrade your Slack client to use messages like these.",
            "color": "#3AA3E3",
            "attachment_type": "default",
            "callback_id": "menu_options_2319",
            "actions": [
                {
                    "name": "games_list",
                    "text": "Pick a game...",
                    "type": "select",
                    "data_source": "external"
                }
            ]
        }
    ]



    sendMessage("Hello from /test", content['channel_id'], content['team_id'], attachments_send=message_attachments)
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
            if key == "help":
                sendHelp(None, curEvent['channel'], curEvent['user'], team_id)
            elif key in commandDict:
                commandDict[key].api_entry(command[len(key)+1:], curEvent['channel'], curEvent['user'], team_id)
            else:
                print("Command Not Found")
                sendHelp("Command \"" + key + "\"" + " Not Found", curEvent['channel'], curEvent['user'], team_id)
    else:
        print("Event not a message")
        print(content)
    return "200"

@app.route("/api/messages/options",methods=['POST'])
def message_option_handle():
    # Parse the request payload
    form_json = json.loads(request.form["payload"])

    menu_options = commandDict[form_json['callback_id']].option_entry(form_json)

    return (Response(json.dumps(menu_options), mimetype='application/json'),200)

@app.route("/api/messages/actions",methods=['POST'])
def message_actions_handle():
    # Parse the request payload
    form_json = json.loads(request.form["payload"])

    # Check to see what the user's selection was and update the message
    commandDict[form_json['callback_id']].action_entry(form_json)

    return make_response("", 200)

@app.route("/api/slash/modify_user_perms", methods=['POST'])
def slash_modify_user_perms():
    content = request.form
    channel = request.form['channel_id']
    user = request.form['user_id']
    team = request.form['team_id']
    if content['token'] != veritoken:
        print("Unauthorized message detected")
        return 401

    args = content['text'].split(" ")
    moduser = args[0][2:11]
    if len(args) != 2:
        print("Invalid number of args")
        sendEphemeral("Invalid number of args", channel, user, team);
    if not checkPermission(user, "owner", team):
        print(user + " attempted to modify permissions of user " + moduser + " to " + args[1])
        sendEphemeral("Access Denied - Must be Owner to change user permissions", channel, user, team)
        return ('', 200)

    if args[1] == Database.permissions.owner.name:
        newPerms = Database.permissions.owner
    elif args[1] == Database.permissions.admin.name:
        newPerms = Database.permissions.admin
    elif args[1] == Database.permissions.user.name:
        newPerms = Database.permissions.user
    else:
        sendEphemeral("Invalid permission name", channel, user, team)
        return('',200)

    dbUser = Database.Users.query.filter_by(user_id = moduser).first()

    if dbUser is None:
        # create new user
        dbWorkspace = Database.Workspaces.query.filter_by(team_id = team).first()
        newUser = Database.Users(newPerms, dbWorkspace.id, moduser)
        Database.db.session.add(newUser)
        Database.db.session.commit()
        print("Created new user", getUserName(moduser, team), "with permissions", newPerms.name)
        sendEphemeral("Created new user " + getUserName(moduser, team) + " with permissions " + newPerms.name, channel, user, team)
    else:
        origPerms = dbUser.permission_level
        dbUser.permission_level = newPerms
        Database.db.session.commit()
        print("Updated user", getUserName(moduser, team), "with permissions", newPerms.name)
        print("Original permissions:", origPerms.name)
        sendEphemeral("Updated user " + getUserName(moduser, team) + " with permissions " + newPerms.name, channel, user, team)
    return make_response("", 200)

@app.route("/api/slash/set_admin_channel",methods=['POST'])
def slash_set_admin_channel():
    channel = request.form['channel_id']
    user = request.form['user_id']
    team_id = request.form['team_id']
    if request.form['token'] != veritoken:
        print("Unauthorized mesage detected")
        return 401

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
def sendMessage (message, sendChannel, team_id, attachments_send=None):
    client,_ = getClient(team_id)
    if client is None:
        print("Team not found: ", team_id)

    if attachments_send is None:
        client.api_call(
            "chat.postMessage",
            channel=sendChannel,
            text=message
            )
    else:
        client.api_call(
            "chat.postMessage",
            channel=sendChannel,
            text=message,
            attachments=attachments_send
            )

''' Function to send an ephemeral message
    Input:
        message: Message to send
        sendChannel: Channel to send the message in
        sendUserID: User to send the message to
    Output:
        N/A
'''
def sendEphemeral (message, sendChannel, sendUserID, team_id, attachments_send=None):
    client,_ = getClient(team_id)

    if client is None:
        print("Team not found: ", team_id)
        return

    client.api_call(
        "chat.postEphemeral",
        channel=sendChannel,
        user=sendUserID,
        text=message,
        attachments=attachments_send
    )

def modifyMessage(orig_ts, message, sendChannel, sendUser, team, attachments_send=None):
    client,_ = getClient(team)

    if client is None:
        print("Team not found: ", team)
        return

    client.api_call(
        "chat.update",
        channel=sendChannel,
        user=sendUser,
        ts=orig_ts,
        text=message,
        attachments=attachments_send
    )

def deleteMessage(ts_delete, chan, team):
    client,_ = getClient(team)

    if client is None:
        print("Team not found: ", team)
        return

    client.api_call(
        "chat.delete",
        channel=chan,
        ts=ts_delete
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

def checkDM(channelCheck, team):
    client,_ = getClient(team)
    if client is None:
        print("Client not found: ", team)
        return False

    response = client.api_call(
        "channels.info",
        channel=channelCheck
        )

    if response['ok']:
        #Channel is a public channel
        return False

    response = client.api_call(
        "groups.info",
        channel=channelCheck
        )

    if response['ok']:
        #Channel is a pivate channel/group message
        return False

    #Channel is a DM
    return True

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
    messageString += "\nModule List:\n"
    for module in commandDict:
        messageString += "\t\"!" + module + "\"\n"

    sendEphemeral(messageString, sendChannel, sendUserID, sendTeamID)

if __name__ == '__main__':
    main()
