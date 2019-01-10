import InfraBot
from InfraModule import InfraModule

class UserManager(InfraModule):
    options = None
    def __init__(self):
        self.num = 0
        super.__init__("user", options)

    def api_entry(self, message, channel, user, team_id):
        InfraBot.sendMessage("Module not yet implemented", channel, team_id)
        return "Module not yet implemented"
