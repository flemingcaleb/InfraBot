from app import InfraBot

def api_entry(message, channel, user, team_id):
    InfraBot.sendEphemeral("AgentManager: Command not implemented", channel, user, team_id)

