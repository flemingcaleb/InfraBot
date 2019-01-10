class InfraModule:
    options = None
    def __init__(self, options):
        self.options = options

    def api_entry(self, message, channel, user, team_id):
        InfraBot.sendMessage("Module not yet implemented", channel, team_id)
        return "Module not yet implemented"

    def action_entry(self, form_data):
        return "Action not implemented"