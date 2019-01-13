import InfraBot
from InfraModule import InfraModule
import Database
from datetime import datetime, timedelta

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
        if message is "":
            # Check if the user is allowed to get a hint
            lastHint = Database.Users.query.filter_by(user_id=user).first()
            curTime = datetime.now()
            if not lastHint is None:
                workspace = InfraBot.getClient(team_id)
                timeFrame = workspace.hint_timeout
                if curTime < (lastHint + timeFrame):
                    response = "You must wait until "
                    response += str(lastHint+timeFrame)
                    response += " for your next hint"
                    InfraBot.sendEphemeral(response, channel, user, team_id)
                    return "Permission Denied"
 
            # Start menu to select hint to give
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
            splitArr = action['name'].split(":")
            name = splitArr[0]
            if len(splitArr) > 1:
                data = splitArr[1]
            else:
                data = None
            if name == "initial_menu":
                if action['selected_options'][0]['value'] == "list":
                    message_text,attachments = self.labs_list(user, channel, team, form_data)
                elif action['selected_options'][0]['value'] == "hint":
                    message_text,attachments = self.labs_hints_list(user, channel, team, form_data)
                elif action['selected_options'][0]['value'] == "submit":
                    message_text,attachments = self.labs_submit(user, channel, team, form_data)
            elif name == "list":
                message_text,attachments = self.labs_hints_categories(user, channel, team, form_data)
            elif name == "categories":
                message_text,attachments = self.labs_hint_selection(user,channel,team, form_data)
            elif name == "hints":
                message_text,attachments = self.labs_hint_dispense(user,channel,team,form_data)
            else:
                message_text = "Other"
                attachments = None

        if InfraBot.checkDM(channel, team):
            InfraBot.sendMessage(message_text, channel, team, attachments_send=attachments)
        else:
            InfraBot.sendEphemeral(message_text, channel, user, team, attachments_send=attachments) 

    def option_entry(self, form_data):
        print("Options:\n", form_data)
        splitArr = form_data['name'].split(":")
        name = splitArr[0]
        if len(splitArr) > 1:
            data = splitArr[1]
        else:
            data = None
        team = form_data['team']['id']
        if name == "list":
            first = True
            newOptions = {}
            newOptions['options'] = []
            results = Database.Labs.query.filter_by(workspace_id = self.workspaces[team]).all()
            if results is None:
                print("Error: No Labs Found")
                return
            else:
                for result in results:
                    newOption = {}
                    newOption['text'] = result.name
                    newOption['value'] = result.id
                    newOptions['options'].append(newOption)
                return newOptions         
        elif name == "categories":
            categories = Database.HintCategories.query.filter_by(lab_id=data).all()
            newOptions = {}
            newOptions['options'] = []
            if categories is None:
                print("Error: No Labs Found")
                return
            else:
                for category in categories:
                    newOption = {}
                    newOption['text'] = category.name
                    newOption['value'] = category.id
                    newOptions['options'].append(newOption)
                return newOptions
        elif name == "hints":
            hints = Database.Hints.query.filter_by(category=data).all()
            newOptions = {}
            newOptions['options'] = []
            if hints is None:
                print("Error: No Hints Found")
                return
            else:
                for hint in hints:
                    newOption = {}
                    newOption['text'] = hint.seq_num
                    newOption['value'] = hint.id
                    newOptions['options'].append(newOption)
                return newOptions
        return self.options

    def labs_list(self, user, channel, team, form):
        resultString = ""

        results = Database.Labs.query.filter_by(workspace_id = self.workspaces[team]).all()
        if results is None:
            resultString = "Error: No Labs Found"
        else:
            for result in results:
                resultString += result.name + " - " + result.url + "\n"

        InfraBot.deleteMessage(form['message_ts'], channel, team)
        return resultString,None

    def labs_hints_list(self, user, channel, team, form):
        InfraBot.deleteMessage(form['message_ts'], channel, team)
        message_attachments = [
            {
                "text": "Select a Lab",
                "fallback": "If you could read this message, you'd be choosing something fun to do right now.",
                "color": "#3AA3E3",
                "attachment_type": "default",
                "callback_id": "lab",
                "actions": [
                    {
                        "name": "list",
                        "text": "Which random bug do you want to resolve?",
                        "type": "select",
                        "data_source": "external",
                    }
                ]
            }
        ]
        return "",message_attachments


    def labs_hints_categories(self, user, channel, team, form):
        print("Categories:\n", form)
        InfraBot.deleteMessage(form['message_ts'], channel, team)
        tempVal = form['actions'][0]['selected_options'][0]['value']
        #print(tempVal)
        message_attachments = [
            {
                "text": "Select a Category from Lab",
                "fallback": "If you could read this message, you'd be choosing something fun to do right now.",
                "color": "#3AA3E3",
                "attachment_type": "default",
                "callback_id": "lab",
                "actions": [
                    {
                        "name": "categories:"+tempVal,
                        "text": "Which random bug do you want to resolve?",
                        "type": "select",
                        "data_source": "external",
                    }
                ],
               "value":"1"
            }
        ]
        return "",message_attachments

    def labs_hint_selection(self, user, channel, team, form):
        print("Hints:\n", form)
        InfraBot.deleteMessage(form['message_ts'], channel, team)
        tempVal = form['actions'][0]['selected_options'][0]['value']
        #print(tempVal)
        message_attachments = [
            {
                "text": "Select a hint number",
                "fallback": "If you could read this message, you'd be choosing something fun to do right now.",
                "color": "#3AA3E3",
                "attachment_type": "default",
                "callback_id": "lab",
                "actions": [
                    {
                        "name": "hints:"+tempVal,
                        "text": "Which random bug do you want to resolve?",
                        "type": "select",
                        "data_source": "external",
                    }
                ],
               "value":"1"
            }
        ]
        return "",message_attachments

    def labs_hint_dispense(self, user, channel, team, form):
        InfraBot.deleteMessage(form['message_ts'], channel, team)
        tempVal = form['actions'][0]['selected_options'][0]['value']

        hint = Database.Hints.query.filter_by(id=tempVal).first()
        lab = Database.Labs.query.filter_by(id=hint.lab_id).first()
        category = Database.HintCategories.query.filter_by(id=hint.category).first()

        message = lab.name+" "
        message += category.name+" "
        message += "#" + str(hint.seq_num) + " - " + hint.hint

        InfraBot.sendEphemeral(message, channel, user, team)
    def labs_submit(self, user, channel, team, form):
        InfraBot.deleteMessage(form['message_ts'], channel, team)
        return "Lab submissions not yet implemented",None
