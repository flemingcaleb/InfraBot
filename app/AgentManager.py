import InfraBot

name = "agent"
options = None

def api_entry(message, channel, user, team_id):
    InfraBot.sendEphemeral("AgentManager: Command not implemented", channel, user, team_id)

def action_entry(self, form_data):
    pass