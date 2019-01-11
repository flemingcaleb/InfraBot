import InfraBot
from InfraModule import InfraModule
import Database

class LabManager(InfraModule):
    def __init__ (self):
        self.workspaces = {}
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

        queries = Database.Status.query.all()

        for workspace in queries:
            dbWorkspace = Database.Workspaces.query.filter_by(id = workspace.workspace).first()
            if dbWorkspace is None:
                print("Workspace does not exist in database")
            else:
                self.workspaces[dbWorkspace.team_id] = workspace.workspace

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

        if not team in self.workspaces:
            if not self.add_workspace_id(team_id):
                print("Workspace does not exist")
                return "Workspace " + team_id + " does not exist"

        for action in form_data["actions"]:
            if action['name'] == "initial_menu":
                print("Form data", form_data)
                print("Action:\n", action)
                if action['selected_options'][0]['value'] == "list":
                    message_text,attachments = self.labs_list(user, channel, team, form_data)
                elif action['selected_options'][0]['value'] == "hint":
                    message_text,attachments = self.labs_hints(user, channel, team, form_data)
                elif action['selected_options'][0]['value'] == "submit":
                    message_text,attachments = self.labs_submit(user, channel, team, form_data)
            else:
                message_text = "Other"
                attachments = None
        if InfraBot.checkDM(channel, team):
            InfraBot.sendMessage(message_text, channel, team, attachments_send=attachments)
        else:
            InfraBot.sendEphemeral(message_text, channel, user, team, attachments_send=attachments) 

    def labs_list(self, user, channel, team, form):
        resultString = ""

        results = Database.Labs.query.filter_by(workspace_id = self.workspaces[team]).all()
        if results is None:
            resultString = "Error: No Labs Found"
        else:
            for result in results:
                resultString = result.name + " - " + result.url + "\n"

        InfraBot.deleteMessage(form['message_ts'], channel, team)
        return resultString,None

    def labs_hints(self, user, channel, team, form):
        InfraBot.deleteMessage(form['message_ts'], channel, team)
        return "Hints not yet implemented",None

    def labs_submit(self, user, channel, team, form):
        InfraBot.deleteMessage(form['message_ts'], channel, team)
        return "Lab submissions not yet implemented",None
