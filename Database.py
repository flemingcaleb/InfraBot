import enum
from InfraBot import InfraBot

db = InfraBot.db

class permissions(enum.Enum):
    owner = 1
    admin = 2
    user = 3

class Workspaces(db.Model):
    def __init__(self, b_tok, a_tok, v_tok, team):
        self.bot_token = b_tok
        self.access_token = a_tok
        self.verify_token = v_tok
        self.team_id = team
    id = db.Column(db.Integer, primary_key=True)
    bot_token = db.Column(db.String(100), nullable=False)
    access_token = db.Column(db.String(100), nullable=False)
    verify_token = db.Column(db.String(100), nullable=False)
    team_id = db.Column(db.String(20), nullable=False)
    users = db.relationship('Users', backref='workspace', lazy=True)
    agents = db.relationship('Agents', backref='workspace', lazy=True)

class Users(db.Model):
    def __init__(self, permission, workspace, user):
        self.permission_level = permission
        self.workspace_id = workspace
        self.user_id = user
    id = db.Column(db.Integer, primary_key=True)
    permission_level = db.Column('permission_level', db.Enum(permissions), nullable=False)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    user_id = db.Column(db.String(20), nullable=False)
    commands = db.relationship('Commands', backref='user', lazy=True)

class Agents(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    permissions_required = db.Column('permissions_required', db.Enum(permissions), nullable=False)
    token = db.Column(db.String(100), nullable=False)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    commands = db.relationship('Commands', backref='agent', lazy=True)

class Commands(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=False)
    command = db.Column(db.Text, nullable=False)
    result = db.Column(db.Text, nullable=True)

