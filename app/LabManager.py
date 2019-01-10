import InfraBot
from InfraModule import InfraModule

class LabManager(InfraModule):
    options = None
    def __init__ (self):
        super.__init__("lab", options)

    def api_entry(self, message, channel, user, team_id):
        pass
        