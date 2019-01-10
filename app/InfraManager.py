import InfraBot
from InfraModule import InfraModule

class InfraManager(InfraModule):
    def __init__(self, options=None):
        self.num = 0
        super().__init__("infra", None)

    def api_entry(self, message, channel, user, team_id):
        InfraBot.sendMessage("Module not yet implemented", channel, team_id)
        return "Module not yet implemented"
