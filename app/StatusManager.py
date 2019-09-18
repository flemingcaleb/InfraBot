import InfraBot
from InfraModule import InfraModule
from Database import status_code as statusType
import Database

class StatusManager(InfraModule):
    
    def __init__ (self):
        super().__init__("status", None)
        self.workspaces = {}
        queries = Database.Status.query.all()

        for workspace in queries:
            dbWorkspace = Database.Workspaces.query.filter_by(id = workspace.workspace).first()
            if dbWorkspace is None:
                print("Workspace does not exist in database")
            else:
                self.workspaces[dbWorkspace.team_id] = workspace.workspace

    def api_entry(self, message, channel, user, team_id):
        if not team_id in self.workspaces:
            if not self.add_workspace_id(team_id):
                print("Workspace does not exist")
                return "Workspace " + team_id + " does not exist"
        curStatus = Database.Status.query.filter_by(workspace = self.workspaces[team_id]).first()
        if curStatus is None:
            # Create new status
            newStatus = Database.Status(self.workspaces[team_id], statusType.GREEN)
            Database.db.session.add(newStatus)
            Database.db.session.commit()
            curStatus = newStatus

        if message is "":
            InfraBot.sendMessage("Status: " + curStatus.status.name, channel, team_id)
            return "Status returned"
        
        if message.startswith("set "):
            remainder = message[len("set "):].upper()
            if remainder.startswith("YELLOW") and curStatus.status == statusType.GREEN:
                curStatus.status = statusType.YELLOW
                InfraBot.notifyAdmins(InfraBot.getUserName(user, team_id) + " set status to YELLOW", team_id)
            else:
                if not InfraBot.checkPermission(user, "admin", team_id):
                    InfraBot.sendHelp("Access Denied", channel, user, team_id)
                    return "Access Denied"
                
                if remainder == "GREEN":
                    curStatus.status = statusType.GREEN
                elif remainder == "ORANGE":
                    curStatus.status = statusType.ORANGE
                elif remainder == "PINK":
                    curStatus.status = statusType.PINK
                elif remainder == "RED":
                    curStatus.status = statusType.RED
                else:
                    InfraBot.sendHelp("Invalid status.", channel, user, team_id)
                    return "Invalid status selected"

                InfraBot.notifyAdmins(InfraBot.getUserName(user, team_id) + " set status set to " + curStatus.status.name, team_id)

            if InfraBot.checkDM(channel, team_id):
                InfraBot.sendMessage("Status: " + curStatus.status.name, channel, team_id)
            else:
                InfraBot.sendEphemeral("Status: " + curStatus.status.name, channel, user, team_id)
            
            Database.db.session.commit()
            return InfraBot.getUserName(user, team_id) + " set status to " + curStatus.status.name
        elif message.startswith("help"):
            self.send_error(None, channel, user, team_id)
        else:
            self.send_error("Invalid command", channel, user, team_id)

    def add_workspace_id(self, team_id):
        dbWorkspace = Database.Workspaces.query.filter_by(team_id = team_id).first()
        if dbWorkspace is None:
            print("Workspace does not exist in database")
            return False
        else:
            self.workspaces[team_id] = dbWorkspace.id
            return True
    
    def send_error(self, message, channel, user, team_id):
        messageString = ""
        if not message is None:
            messageString += message +"\n\n"
        messageString += "Status Help:\n"
        messageString += "\t!status - Prints the current status\n"
        messageString += "\t!status set - Sets the current status (may require admin privileges)\n"
        messageString += "\t!status help - Prints this help prompt\n"
        messageString += "\nStatus Meaning:\n"
        messageString += "\tGREEN: All systems functioning as expected\n"
        messageString += "\tYELLOW: User reported warning. Not yet confirmed by support\n"
        messageString += "\tORANGE: Support confirmed issue impacting user experience. VPN and user VMS still accessible\n"
        messageString += "\tPINK: Support confirmed issue impacting user experience and VPN access. User VMs still accessible via lab and/or Wifi\n"
        messageString += "\tRED: Support confirmed issue impacting all services. Virtual Range is inaccessible\n"

        InfraBot.sendEphemeral(messageString, channel, user, team_id)
