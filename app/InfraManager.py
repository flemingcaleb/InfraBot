import InfraBot

class InfraManager:
    def __init__(self):
        self.num = 0

    def api_entry(self, message, channel, user, team_id):
        InfraBot.sendMessage("Module not yet implemented", channel, team_id)
        return "Module not yet implemented"
