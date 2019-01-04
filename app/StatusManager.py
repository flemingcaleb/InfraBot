import InfraBot
from Database import status_code as statusType
import Database

class StatusManager:
    workspaces = {}
    def __init__ (self):
        queries = Database.Status.query.all();
        for workspace in queries:
            print("Workspace: ", queries[0].workspace)
            print("Status: ", queries[0].status)
            dbWorkspace = Database.Workspaces.query.filter_by(id = workspace.workspace).first()
            if dbWorkspace is None:
                print("Workspace does not exist in database")
            else:
                self.workspaces[dbWorkspace.team_id] = workspace.workspace
        
        print(self.workspaces)

    def api_entry(self, message, channel, user, team_id):
        if not team_id in self.workspaces:
            if not self.add_workspace_id(team_id):
                print("Workspace does not exist")
                return "Workspace " + team_id + " does not exist"
        curStatus = Database.Status.query.filter_by(workspace = self.workspaces[team_id]).first()
        if curStatus is None:
            # Create new status
            pass

        if message is "":
            InfraBot.sendMessage("Status: " + curStatus.status.name, channel, team_id)
            return "Status returned"
        
        if message.startswith("set "):
            remainder = message[len("set "):].upper()
            if remainder.startswith("YELLOW") and curStatus.status == statusType.GREEN:
                curStatus.status = statusType.YELLOW
            else:
                if not InfraBot.checkPermission(user, "admin", team_id):
                    InfraBot.send_error("Access Denied", channel, user, team_id)
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
                    InfraBot.send_error("Invalid status.", channel, user, team_id)
                    return "Invalid status selected"

            InfraBot.sendEphemeral("Status: " + curStatus.status.name, channel, user, team_id)
            Database.db.session.commit()
            return "Set status to " + curStatus.status.name
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
