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
  -----------------------------------------------------------------------------------
