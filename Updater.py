from InfraBot import InfraBot
from InfraBot import db
from InfraBot import Database

class Updater:
    def api_entry(self, message, channel, user, team_id):
        if message.startswith("in "):
            #Schedule reminder in X minutes

        elif message.startswith("every "):
            #Schedule reminder every X minutes

        elif message.startswith("for "):
            #Schedule reminder for N time every day

        elif message == "list":
            #List all recurring tasks
        
        elif message.startswith("stop ")
            #Stop reminder with the given ID
        
        else:
            return "Command not found"
