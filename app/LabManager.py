import InfraBot
from InfraModule import InfraModule

class LabManager(InfraModule):
    def __init__ (self):
        menu_options = {
            "options": [
                {
                    "text": "Chess",
                    "value": "chess"
                },
                {
                    "text": "Global Thermonuclear War",
                    "value": "war"
                }
            ]
        }
        super().__init__("lab", menu_options)

    def api_entry(self, message, channel, user, team_id):
        message_attachments = [
            {
                "text": "Lab Menu",
                "fallback": "If you could read this message, you'd be choosing something fun to do right now.",
                "color": "#3AA3E3",
                "attachment_type": "default",
                "callback_id": "lab",
                "actions": [
                    {
                        "name": "initial_menu",
                        "text": "Select an option...",
                        "type": "select",
                        "options": [
                            {
                                "text": "List",
                                "value": "list"
                            },
                            {
                                "text": "Hint",
                                "value": "hint"
                            },
                            {
                                "text": "Submit",
                                "value": "submit"
                            }
                        ]
                    }
                ]
            }
        ]
        if InfraBot.checkDM(channel, team_id):
            InfraBot.sendMessage("", channel, team_id, attachments_send=message_attachments)
        else:
            InfraBot.sendEphemeral("", channel, user, team_id, attachments_send=message_attachments)
        return "Initial Lab"

    def action_entry(self, form_data):
        channel = form_data['channel']['id']
        user = form_data['user']['id']
        team = form_data['team']['id']

        for action in form_data["actions"]:
            if action['name'] == "initial_menu":
                message_text = "Initial Menu"
                attachments = None
            else:
                message_text = "Other"
                attachments = None
        if InfraBot.checkDM(channel, team):
            InfraBot.sendMessage(message_text, channel, team, attachments_send=attachments)
        else:
            InfraBot.sendEphemeral(message_text, channel, user, team, attachments_send=attachments) 
