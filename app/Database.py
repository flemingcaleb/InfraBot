import enum
import InfraBot

db = InfraBot.db

class permissions(enum.Enum):
    owner = 1
    admin = 2
    user = 3

class update_type(enum.Enum):
    IN = 1
    EVERY = 2
    FOR = 3

class status_code(enum.Enum):
    GREEN = 1
    YELLOW = 2
    ORANGE = 3
    PINK = 4
    RED = 5

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
    admin_channel = db.Column(db.String(20), nullable=True)
    users = db.relationship('Users', backref='workspace', lazy=True)
    agents = db.relationship('Agents', backref='workspace', lazy=True)
    updates = db.relationship('Updates', backref='workspace', lazy=True)
    #status = db.relationship('', backref='workspace', lazy=True)

class Status(db.Model):
    def __init__(self, workspace_id, initStatus):
        self.workspace = workspace_id
        self.status = initStatus

    workspace = db.Column(db.Integer, db.ForeignKey('workspaces.id'), primary_key=True)
    status = db.Column('status', db.Enum(status_code), nullable=False)

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
    updates = db.relationship('Updates', backref='user', lazy=True)

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

class Updates(db.Model):
    def __init__(self, n_reminder, n_channel_id, n_type, n_time, n_user_id, n_workspace_id):
        self.reminder = n_reminder
        self.channel_id = n_channel_id
        self.type = n_type
        self.time = n_time
        self.user_id = n_user_id
        self.workspace_id = n_workspace_id

    id = db.Column(db.Integer, primary_key=True)
    reminder = db.Column(db.String(100), nullable = False)
    channel_id = db.Column(db.String(20), nullable = False)
    type = db.Column('type', db.Enum(update_type), nullable=False)
    time = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)

# Models for the lab module
class Labs(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    url = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.Integer, nullable=True)
    possible_score = db.Column(db.Integer, nullable=True)

class LabScores(db.Model):

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    lab_id = db.Column(db.Integer, db.ForeignKey('labs.id'), primary_key=True)
    score = db.Column(db.Integer, nullable=False)

class HintCategories(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    lab_id = db.Column(db.Integer, db.ForeignKey('labs.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    num_of_hints = db.Column(db.Integer, nullable=False)

class Hints(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    lab_id = db.Column(db.Integer, db.ForeignKey('labs.id'), nullable=False)
    category = db.Column(db.Integer, db.ForeignKey('hintcategories.id'), nullable=False)
    seq_num = db.Column(db.Integer, nullable=False)
    hint = db.Column(db.Text, nullable=False)
