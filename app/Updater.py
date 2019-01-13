import threading
from time import sleep
import InfraBot
from InfraModule import InfraModule
import Database

db = InfraBot.db

class Updater(InfraModule):
    def __init__(self):
        super().__init__("update", None)

    def api_entry(self, message, channel, user, team_id):
        if message.startswith("in "):
            remainder = message[len("in "):]
            splitNum = remainder.split(' ', 1)
            number = int(splitNum[0])

            self.__inReminder = Updater_InThread(splitNum[1], number, channel, team_id)
            self.__inReminder.start()
            #Schedule reminder in X minutes
            InfraBot.sendEphemeral("Update Scheduled", channel, user, team_id)
            return "Reminder Scheduled"

        elif message.startswith("every "):
            #Schedule reminder every X minutes
            InfraBot.sendEphemeral("Command Not Found: 'every'", channel, user, team_id)
            return "Command not yet found"

        elif message.startswith("for "):
            #Schedule reminder for N time every day
            InfraBot.sendEphemeral("Command Not Found: 'for'", channel, user, team_id)
            return "Command not yet found"

        elif message == "list":
            #List all recurring tasks
            InfraBot.sendEphemeral("Command Not Found: 'list'", channel, user, team_id)
            return "Command not yet found"

        elif message.startswith("stop "):
            #Stop reminder with the given ID
            InfraBot.sendEphemeral("Command Not Found: 'list'", channel, user, team_id)
            return "Command not yet found"

        else:
            InfraBot.sendEphemeral("Command Not Found", channel, user, team_id)
            return "Command not found"

''' Updater to handle a single update in the future '''
class Updater_InThread(threading.Thread):
    ''' Function to initialize the thread with the time to wait and message information '''
    def __init__(self, message, time, channel, workspace):
        threading.Thread.__init__(self)
        self.waitTime = time
        self.updateMessage = message
        self.updateChannel = channel
        self.updateWorkspace = workspace

    ''' Function that waits for the configured amount of time and then sends the configured
        message on the given channel in the given workspace '''
    def run(self):
        sleep(self.waitTime * 60)
        InfraBot.sendMessage(self.updateMessage, self.updateChannel, self.updateWorkspace)
