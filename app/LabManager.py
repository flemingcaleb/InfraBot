import InfraBot
from InfraModule import InfraModule

class LabManager(InfraModule):
    def __init__ (self):
        super().__init__("lab", None)

    def api_entry(self, message, channel, user, team_id):
        pass
        
