# InfraBot

This project is a slackbot designed for the K-State Cyber Defense Club to help in the management of club activities. This project is designed to allow the club to enable members to get up-to-date information about the KSUCDC Virtual Range and many of the learning opportunities that are a part of that. 

Currently the project contains several different modules:
 - status - Allows users to access up-to-date status information of the Virtual Range as well as report any suspected issues to the system administration staff
 - dante - Provides users with updates on the status of Dantes Forest, one of the many learning opportunities that are a part of the Virtual Range

These modules are implemented as commands that may be accessed using the format "!\<module name\>" in any slack message that is readable by InfraBot (either in a channel where InfraBot is a member, or a DM directly to InfraBot). InfraBot may respond with either a message readable to the entire channel or directly to the user with an ephemeral message.

In addition to these commands, InfraBot installs several slash commands to the workspace. These slash commands serve as a method to configure InfraBot itself, while the message commands above are how to interact with InfraBot.

-----------------------------------------------------------------------
## Permissions
User Permissions are divided into 3 categories:
  - Owner
  - Admin
  - User

These permissions are initially inherited from slack itself (owners and admins being default groups on even free slack plans). After the user uses InfraBot for the first time the permissions level is stored independently of Slack and may be modified as needed to give users more or less permissions.

The permissions of the user may be checked at any time using the checkPermissions helper function.

-----------------------------------------------------------------------
## Slack API
- /test : Tests connection to app from workspace
- /api/messages : URI for event notifications
- /api/slash/set_admin_channel : URI for slash command to set the current channel as the admin channel for the workspace
- /install  : URI for app installation to new workspaces
- /install/confirm : URI for second step of app installation on new workspaces

-----------------------------------------------------------------------
## Agent API
- /api/agent/\<id\>/command : Allows a registered agent to fetch a list of pending command IDs
- /api/agent/\<aid\>/command/\<cid\> : Allows a registered agent to GET the command corresponding to <cid> and POST the results from command id <cid>

-----------------------------------------------------------------------
## Module API
Must provide function:
  
  api_entry(message, channel, user) - Returns message to be logged
  
Provided helper functions:
 Function                                                    | Returns | Description
 :---------------------------------------------------------- | :-----: | :----
 sendMessage(message, sendChannel, team_id)                  | N/A     | Sends given message to provided channel
 sendEphemeral(message, sendChannel, sendUserID, team_id)    | N/A     | Sends ephemeral message to the given user in the given channel
 notifyAdmins(message, team_id)                              | Boolean | Sends a message to the designated admin channel for the given workspace, returns a boolean indicating if the admins have been notified (false if the admin channel not set)
 checkPermission(user, requiredPerms, team_id)               | Boolean | Checks to see if the given user possesses the specified permissions. Returns true/false
 getUserName(user_id, team_id)                               | String  | Returns the username of the given user
 checkDM(channel, team_id)				     | Boolean | Checks to see if the given channel is a DM with InfraBot
 deleteMessage(ts_to_delete, channel, team)		     | N/A     | Delete given message

-----------------------------------------------------------------------
## Database Schema
### Table: users
 Column Name      | Type        | Notes   
 :--------------: | :---------: | :-------
 id               | int         |         
 permission_level | permissions | enum    
 workspace_id     | int         | FOREIGN KEY to workspaces.id 
 user_id          | varchar(20) |          
  
### Table: workspaces
 Column Name      | Type        | Notes   
 :--------------: | :---------: | :-------
 id               | int         |         
 bot_token        | varchar(100)|     
 access_token     | varchar(100)|  
 verify_token     | varchar(100)|
 team_id          | varchar(20) |
 admin_channel    | varchar(20) |

### Table: status
 Column Name          | Type        | Notes
 :------------------: | :---------: | :-------
 workspace            | int         | FOREIGN KEY TO workspaces.id
 status               | status_code | enum

### Table: agents
 Column Name          | Type        | Notes   
 :------------------: | :---------: | :-------
 id                   | int         |         
 permissions_required | permissions | enum    
 token                | varchar(100)|
 workspace_id         | int         | FOREIGN KEY to workspaces.id
 
### Table: commands
 Column Name      | Type        | Notes   
 :--------------: | :---------: | :-------
 id               | int         |         
 user_id          | int         | FOREIGN KEY to users.id    
 agent_id         | int         | FOREIGN KEY to agents.id 
 command          | text        |
 result           | text        |
 
 ### Table: updates
 | Column Name    | Type        | Notes
 | :------------: | :---------: | :--------
 | id             | int         |
 | reminder       | varchar(100)| String containing the update to send *NOTE: Max length is 100 characters*
 | channel_id     | varchar(20) | String indicating the channel to send the update to
 | type           | update_type | enum
 | time           | int         | Int indicating the number of minutes between updates or minutes after midnight to update
 | user_id        | int         | FOREIGN KEY to users.id
 | workspace_id   | int         | FOREIGN KEY to workspaces.id
 
 ### Enum: permissions
  |  Value  |
  | :-----: |
  | 'owner' |
  | 'admin' |
  | 'user'  |
  
  ### Enum: update_type
  |  Value  |
  | :-----: |
  |   'in'  |
  | 'every' |
  |  'for'  |

  ### Enum: status_code
  | Value  |
  | :----: |
  | GREEN  |
  | YELLOW |
  | ORANGE |
  |  PINK  |
  |  Red   |

  -----------------------------------------------------------------------------------
