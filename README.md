# InfraBot
-----------------------------------------------------------------------
## Slack API
- /test : Tests connection to app from workspace
- /api/messages : URI for event notifications
-----------------------------------------------------------------------
## Agent API
- /api/agent/\<id\>/command : Allows a registered agent to fetch a list of pending command IDs
- /api/agent/\<aid\>/command/\<cid\> : Allows a registered agent to GET the command corresponding to <cid> and POST the results from command id <cid>
-----------------------------------------------------------------------
## Module API
Must provide function:
  
  api_entry(message, channel, user) - Returns message to be logged
  
Provided helper functions:
  - sendMessage(message, sendChannel) - sends given message to provided channel
  - sendEphemeral(message, sendChannel, sendUserID) - sends ephemeral message to the given user in the given channel
  - checkPermission(user, requiredPerms) - checks to see if the given user possesses the specified permissions. Returns true/false
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
 
 ### Enum: permissions
  |  Value  |
  | :-----: |
  | 'owner' |
  | 'admin' |
  | 'user'  |
  -----------------------------------------------------------------------------------
