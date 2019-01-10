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
                "fallback": "Upgrade your Slack client to use messages like these.",
                "color": "#3AA3E3",
                "attachment_type": "default",
                "callback_id": "menu_options_2319",
                "actions": [
                    {
                        "name": "lab",
                        "text": "Pick a game...",
                        "type": "select",
                        "data_source": "external"
                    }
                ]
            }
        ]

        InfraBot.sendMessage("Hello from /test", channel, team_id, attachments_send=message_attachments)
        return "Initial Lab"

    def action_entry(self, form_data):
        selection = form_data["actions"][0]["selected_options"][0]["value"]

        if selection == "war":
            message_text = "The only winning move is not to play.\nHow about a nice game of chess?"
        else:
            message_text = ":horse:"

        print("\n\n\n\n\n\n\n------------------------------")
        print(form_data['team']['id'])
        client,_ = InfraBot.getClient(form_data['team']['id'])
        if client is None:
            print("Team not found: ", team_id)

        response = client.api_call(
        "chat.update",
        channel=form_data["channel"]["id"],
        ts=form_data["message_ts"],
        text=message_text,
        attachments=[]
        )
