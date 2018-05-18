from app import InfraBot
from app import db
from app import Database

class Updater:
    def api_entry(self, message, channel, user, team_id):
        if message.startswith("in "):
            #Schedule reminder in X minutes
            sendEphemeral("Command Not Found: 'in'", channel, user, team_id)
            return "Command not yet found"

        elif message.startswith("every "):
            #Schedule reminder every X minutes
            sendEphemeral("Command Not Found: 'every'", channel, user, team_id)
            return "Command not yet found"

        elif message.startswith("for "):
            #Schedule reminder for N time every day
            sendEphemeral("Command Not Found: 'for'", channel, user, team_id)
            return "Command not yet found"

        elif message == "list":
            #List all recurring tasks
            sendEphemeral("Command Not Found: 'list'", channel, user, team_id)
            return "Command not yet found"
        
        elif message.startswith("stop ")
            #Stop reminder with the given ID
            sendEphemeral("Command Not Found: 'list'", channel, user, team_id)
            return "Command not yet found"
        
        else:
            sendEphemeral("Command Not Found", channel, user, team_id)
            return "Command not found"
