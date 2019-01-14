import InfraBot
from InfraModule import InfraModule
import Database
from datetime import datetime, timedelta

class LabManager(InfraModule):
    def __init__ (self):
        self.workspaces = {}
        
        #default menu options
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

    ''' Module entry point for initial commands
        Input:
            message: Command for the module (minus the '!lab')
            channel: Channel the command originated in
            user: UserID that issued the command
            team_id: TeamID the command is from

        Output:
            String to be logged by the InfraBot core
    '''
    def api_entry(self, message, channel, user, team_id):
        if message is "":
            # Start menu to select hint to give
            if not InfraBot.checkPermission(user, "user", team_id):
                InfraBot.sendEphemeral("Permission Denied", channel, user,team_id)
                return "!lab - Permission Denied: User " + user
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

        elif message.startswith("hint reset "):
            # Handle command to reset the hint lockout for a user
            if not InfraBot.checkPermission(user, "admin", team_id):
                InfraBot.sendEphemeral("Permission Denied", channel, user,team_id)
                return "!lab hint reset - Permission Denied: User " + user

            remainder = message[len("hint reset "):]
            curUser = Database.Users.query.filter_by(user_id=remainder[2:-1]).first()
            curUser.last_hint = None
            Database.db.session.commit()
            InfraBot.sendEphemeral("Reset hint timer for " + InfraBot.getUserName(remainder[2:-1],team_id), channel, user, team_id)
            return "Reset hint timer for " + InfraBot.getUserName(remainder[2:-1],team_id)
       
        elif message.startswith("set timeout "):
            # Set the workspace hint lockout
            if not InfraBot.checkPermission(user, "owner", team_id):
                InfraBot.sendEphemeral("Permission Denied", channel, user,team_id)
                return "!lab hint reset - Permission Denied: User " + user
            
            # Retrieve the number of minutes for the hint timeout from the command
            remainder = message[len("set timeout "):]
            try:
                newTimeout = int(remainder)
            except:
                self.send_error("<number> must be an integer!", channel, user, team_id)
                return "!lab set timeout - Number not integer"

            curWorkspace = Database.Workspaces.query.filter_by(team_id = team_id).first()
            if curWorkspace is None:
                print("Workspace not found")
                return "Workspace not found"

            # Database stores hint_timeout in seconds, command input is in minutes
            curWorkspace.hint_timeout = newTimeout*60
            Database.db.session.commit()
            InfraBot.sendEphemeral("Set timeout to " + str(newTimeout) + " minutes", channel, user, team_id)
            return "Set workspace timeout for workspace " + team_id + " to " + str(newTimeout) + "minutes"
        else:
            self.send_error("Invalid Command", channel, user, team_id)
            return "Command not found"
    
    ''' Module entry point for interactive action responses
        Input:
        form_data: Payload of the message sent as a result of 
            the interactive message
        
        Output: N/A
    '''
    def action_entry(self, form_data):
        channel = form_data['channel']['id']
        user = form_data['user']['id']
        team = form_data['team']['id']

        if not team in self.workspaces:
            if not self.add_workspace_id(team_id):
                print("Workspace does not exist")
                return "Workspace " + team + " does not exist"

        for action in form_data["actions"]:
            # Separate true action name from previously selected option
            splitArr = action['name'].split(":")
            name = splitArr[0]
            if len(splitArr) > 1:
                data = splitArr[1]
            else:
                data = None

            # Determine if user wants list, hint, or to submit
            if name == "initial_menu":
                if action['selected_options'][0]['value'] == "list":
                    message_text,attachments = self.labs_list(user, channel, team, form_data)
                elif action['selected_options'][0]['value'] == "hint":
                    # Check if the user is allowed to get a hint
                    curUser = Database.Users.query.filter_by(user_id=user).first()
                    curWorkspace = Database.Workspaces.query.filter_by(team_id = team).first()
                    curTime = datetime.now()
                    lastHint = curUser.last_hint
                    if not lastHint is None:
                        if curWorkspace is None:
                            print("Workspace is None")
                            InfraBot.deleteMessage(form_data['message_ts'], channel, team)
                            return""
                        timeFrame = timedelta(seconds=curWorkspace.hint_timeout)
                        if curTime < (lastHint + timeFrame):
                            response = "You must wait "
                            response += str((lastHint+timeFrame)-curTime)
                            response += " until your next hint"
                            InfraBot.deleteMessage(form_data['message_ts'], channel, team)
                            InfraBot.sendEphemeral(response, channel, user, team)
                            return ""
                    
                    #Set time that user last got hint
                    curUser.last_hint = datetime.now()
                    Database.db.session.commit()

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

    ''' Module entry point for dynamic options for interactive actions
        Input:
        form_data: Payload of the message sent as a result of 
            the interactive message

        Output:
            Object that when json.dumped contains the properly formatted
            options for the specified interactive messages
    '''
    def option_entry(self, form_data):
        # Separate true action name from previously selected option
        splitArr = form_data['name'].split(":")
        name = splitArr[0]
        if len(splitArr) > 1:
            data = splitArr[1]
        else:
            data = None
        team = form_data['team']['id']
    
        if name == "list":
            # List possible labs as options
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
            # List possible categories from the selected lab
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
            # List hint numbers from the selected category
            hints = Database.Hints.query.filter_by(category=data).all()
            newOptions = {}
            newOptions['options'] = []
            if hints is None:
                print("Error: No Hints Found")
                return
            else:
                for hint in hints:
                    newOption = {}
                    newOption['text'] = "Hint #" + str(hint.seq_num)
                    newOption['value'] = hint.id
                    newOptions['options'].append(newOption)
                return newOptions
        return self.options

    ''' Function that generates a list of labs and their URLs
        Input:
            user: User that requested the lab listing
            channel: Channel to post the listing in
            team: Team whose labs to query
            form: The entirety of the form data from the request

        Output:
            A tuple with the message and any attachments to send.
            The message will be a newline separated list of labs
            and the attachments will be None
    '''
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

    ''' Function that creates the needed attachment to ask the user
        which lab they would like a hint for

        Input:
            user: User that requested the lab listing
            channel: Channel to post the listing in
            team: Team whose labs to query
            form: The entirety of the form data from the request

        Output:
            A tuple with the message and attachments to send. The 
            message will be empty string and the attachments will 
            be the json formatted attachment with the proper action 
            name ("list") to continue the workflow in the action_entry
            function.
    '''
    def labs_hints_list(self, user, channel, team, form):
        InfraBot.deleteMessage(form['message_ts'], channel, team)
        message_attachments = [
            {
                "text": "For which lab would you like a hint?",
                "fallback": "If you could read this message, you'd be choosing something fun to do right now.",
                "color": "#3AA3E3",
                "attachment_type": "default",
                "callback_id": "lab",
                "actions": [
                    {
                        "name": "list",
                        "text": "Select a Lab",
                        "type": "select",
                        "data_source": "external",
                    }
                ]
            }
        ]
        return "",message_attachments

    ''' Function that creates the needed attachment to ask the user
        which category of hint they want from their selected lab

        Input:
            user: User that requested the lab listing
            channel: Channel to post the listing in
            team: Team whose labs to query
            form: The entirety of the form data from the request

        Output:
            A tuple with the message and attachments to send. The 
            message will be empty string and the attachments will 
            be the json formatted attachment with the proper action 
            name ("categories:<value>") to continue the workflow in 
            the action_entry function. The <value> indicates the lab
            the user selected in the previous dialog.
    '''
    def labs_hints_categories(self, user, channel, team, form):
        InfraBot.deleteMessage(form['message_ts'], channel, team)
        tempVal = form['actions'][0]['selected_options'][0]['value']
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
                        "text": "Select Category",
                        "type": "select",
                        "data_source": "external",
                    }
                ],
               "value":"1"
            }
        ]
        return "",message_attachments

    ''' Function that creates the needed attachment to ask the user
        which hint number they want from their selected lab and
        category.

        Input:
            user: User that requested the lab listing
            channel: Channel to post the listing in
            team: Team whose labs to query
            form: The entirety of the form data from the request

        Output:
            A tuple with the message and attachments to send. The 
            message will be empty string and the attachments will 
            be the json formatted attachment with the proper action 
            name ("hints:<value>") to continue the workflow in 
            the action_entry function. The <value> indicates the 
            category the user selected in the previous dialog.
    '''
    def labs_hint_selection(self, user, channel, team, form):
        InfraBot.deleteMessage(form['message_ts'], channel, team)
        tempVal = form['actions'][0]['selected_options'][0]['value']
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
                        "text": "Select Hint Number",
                        "type": "select",
                        "data_source": "external",
                    }
                ],
               "value":"1"
            }
        ]
        return "",message_attachments

    ''' Function that fethes the requested hint for the lab and
        category selected by the user in the previous messages.

        Input:
            user: User that requested the lab listing
            channel: Channel to post the listing in
            team: Team whose labs to query
            form: The entirety of the form data from the request

        Output:
            A tuple with the message and attachments to send. The 
            message will contain the text of the hint selected by the 
            user throughout the previous workflow. The attachments will
            be None.
    '''
    def labs_hint_dispense(self, user, channel, team, form):
        InfraBot.deleteMessage(form['message_ts'], channel, team)
        tempVal = form['actions'][0]['selected_options'][0]['value']

        hint = Database.Hints.query.filter_by(id=tempVal).first()
        lab = Database.Labs.query.filter_by(id=hint.lab_id).first()
        category = Database.HintCategories.query.filter_by(id=hint.category).first()

        message = lab.name+" "
        message += category.name+" "
        message += "#" + str(hint.seq_num) + " - " + hint.hint

        return message,None
    
    ''' Function that will generate the start of the submit lab workflow
        at a later date.

        Input:
            user: User that requested the lab listing
            channel: Channel to post the listing in
            team: Team whose labs to query
            form: The entirety of the form data from the request

        Output:
            A tuple with the message and attachments to send. The 
            message will contain a prompt indicating that submissions
            are not yet supported and the attachments will be None.
    '''
    def labs_submit(self, user, channel, team, form):
        InfraBot.deleteMessage(form['message_ts'], channel, team)
        return "Lab submissions not yet implemented",None

    ''' Function that sends an error/help prompt to the user

        Input:
            message: Error message to send to the user, ommitted if None
            channel: Destination channel of the error message
            user: Recipient of the error message
            team_id: Team in which to send the message

        Output:
            N/A
    '''
    def send_error(self, message, channel, user, team_id):
        messageString = ""
        if not message is None:
            messageString += message +"\n\n"
        messageString += "Lab Help:\n"
        messageString += "\t!lab - Open the interactive lab menu\n"
        messageString += "\t!lab hint reset <user> - Reset the hint timer for the given user (requires admin privileges)\n"
        messageString += "\t!lab set timeout <number> - Sets the workspace hint timeout to <number> minutes"
        messageString += "\t!lab help - Prints this help prompt\n"

        InfraBot.sendEphemeral(messageString, channel, user, team_id)
