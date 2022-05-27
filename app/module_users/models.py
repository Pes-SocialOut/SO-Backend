from email.policy import default
from app import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

# Define a User model
class User(db.Model):
    __tablename__ = 'users'

    # User id
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    # Username
    username = db.Column(db.String, nullable=False)
    # Email
    email = db.Column(db.String, unique=True, nullable=False)
    # User description / information
    description = db.Column(db.String, default="", nullable=False)
    # User hobbies
    hobbies = db.Column(db.String, default="", nullable=False)

    # To CREATE an instance of a User
    def __init__(self, id, username, email, description, hobbies):
        self.id = id
        self.username = username
        self.email = email
        self.description = description
        self.hobbies = hobbies

    def __repr__(self):
        return f'User({self.id}, {self.username}, {self.description}, {self.hobbies})'

    # To DELETE a row from the table
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    # To SAVE a row from the table
    def save(self):
        db.session.add(self)
        db.session.commit()

    def toJSON(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'description': self.description,
            'hobbies': self.hobbies
        }

class SocialOutAuth(db.Model):
    __tablename__ = 'social_out_auth'

    # User id
    id = db.Column(UUID(as_uuid=True), db.ForeignKey(User.id), primary_key=True, default=uuid.uuid4())
    # Salt
    salt = db.Column(db.String, nullable=False)
    # Hashed and salted password
    pw = db.Column(db.String, nullable=False)

    # To CREATE an instance of a SocialOutUser
    def __init__(self, id, salt, pw):
        self.id = id
        self.salt = salt
        self.pw = pw

    def __repr__(self):
        return f'User({self.id}, {self.salt}, {self.pw})'

    # To DELETE a row from the table
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    # To SAVE a row from the table
    def save(self):
        db.session.add(self)
        db.session.commit()

class EmailVerificationPendant(db.Model):
    __tablename__ = 'email_verification'

    email = db.Column(db.String, primary_key=True, nullable=False)
    code = db.Column(db.String, nullable=False)
    expires_at = db.Column(db.DateTime)

    def __init__(self, email, code, expires_at):
        self.email = email
        self.code = code
        self.expires_at = expires_at

    def __repr__(self):
        return f'User({self.email}, {self.code}, {self.expires_at})'

    # To DELETE a row from the table
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    # To SAVE a row from the table
    def save(self):
        db.session.add(self)
        db.session.commit()

class GoogleAuth(db.Model):
    __tablename__ = 'google_auth'

    # User id
    id = db.Column(UUID(as_uuid=True), db.ForeignKey(User.id), primary_key=True, default=uuid.uuid4())
    # Google access token
    access_token = db.Column(db.String, nullable=False)

    # To CREATE an instance of a GoogleUser
    def __init__(self, id, access_token):
        self.id = id
        self.access_token = access_token

    def __repr__(self):
        return f'User({self.id}, {self.access_token})'

    # To DELETE a row from the table
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    # To SAVE a row from the table
    def save(self):
        db.session.add(self)
        db.session.commit()

class FacebookAuth(db.Model):
    __tablename__ = 'facebook_auth'

    # User id
    id = db.Column(UUID(as_uuid=True), db.ForeignKey(User.id), primary_key=True, default=uuid.uuid4())
    # facebook access token
    access_token = db.Column(db.String, nullable=False)

    # To CREATE an instance of a facebookUser
    def __init__(self, id, access_token):
        self.id = id
        self.access_token = access_token

    def __repr__(self):
        return f'User({self.id}, {self.access_token})'

    # To DELETE a row from the table
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    # To SAVE a row from the table
    def save(self):
        db.session.add(self)
        db.session.commit()

class Achievement(db.Model):
    __tablename__ = 'achievements'

    # Achievement id
    id = db.Column(db.String, primary_key=True)
    # Title
    title = db.Column(db.String, nullable=False)
    # Description
    description = db.Column(db.String, nullable=False)
    # Number of stages to be completed
    stages = db.Column(db.Integer, nullable=False, default=1)

    # To CREATE an instance of a Achievement
    def __init__(self, id, title, description, stages):
        self.id = id
        self.title = title
        self.description = description
        self.stages = stages

    def __repr__(self):
        return f'Achievement({self.id}, {self.title}, {self.description}, {self.stages})'

    # To DELETE a row from the table
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    # To SAVE a row from the table
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    @staticmethod
    def getAchievementsOfUserId(id):
        achievement_list = []
        query_result = db.session.query(Achievement, AchievementProgress) \
            .join(AchievementProgress, Achievement.id == AchievementProgress.achievement) \
            .filter(AchievementProgress.user == id) \
            .all()
        for achievement, progress in query_result:
            achievement_item = {
                'id': achievement.id,
                'title': achievement.title,
                'description': achievement.description,
                'stages': achievement.stages,
                'progress': progress.progress,
            }
            if progress.progress == achievement.stages:
                achievement_item['completed_at'] = progress.completed_at
            achievement_list.append(achievement_item)
        return achievement_list

class AchievementProgress(db.Model):
    __tablename__ = 'achievement_progress'

    # User id
    user = db.Column(UUID(as_uuid=True), db.ForeignKey(User.id), primary_key=True, default=uuid.uuid4())
    # Achievement id
    achievement = db.Column(db.String, db.ForeignKey(Achievement.id), primary_key=True)
    # Progreso
    progress = db.Column(db.Integer, nullable=False, default=0)
    # Fecha completado
    completed_at = db.Column(db.DateTime)

    def __init__(self, user, achievement, progress, completed_at):
        self.user = user
        self.achievement = achievement
        self.progress = progress
        self.completed_at = completed_at

    def __repr__(self):
        return f'Achievement({self.id}, {self.achievement}, {self.progress}, {self.completed_at})'

    # To DELETE a row from the table
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    # To SAVE a row from the table
    def save(self):
        db.session.add(self)
        db.session.commit()


class Friend(db.Model):
    __tablename__ = 'friends'
    __table_args__ = (
        db.CheckConstraint('invitee <> invited'),
    )

    # Invitee id
    invitee = db.Column(UUID(as_uuid=True), db.ForeignKey(User.id), primary_key=True, default=uuid.uuid4())
    # Invited id
    invited = db.Column(UUID(as_uuid=True), db.ForeignKey(User.id), primary_key=True, default=uuid.uuid4())

    def __init__(self, invitee, invited):
        self.invitee = invitee
        self.invited = invited

    def __repr__(self):
        return f'Achievement({self.invitee}, {self.invited})'

    # To DELETE a row from the table
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    # To SAVE a row from the table
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    @staticmethod
    def getFriendsOfUserId(id):
        return db.session.query(User) \
            .join(Friend, Friend.invitee == User.id) \
            .filter(Friend.invited == id) \
            .union( db.session.query(User) \
                .join(Friend, Friend.invited == User.id) \
                .filter(Friend.invitee == id) \
            ).all()

class FriendInvite(db.Model):
    __tablename__ = 'friend_invites'

    invitee = db.Column(UUID(as_uuid=True), db.ForeignKey(User.id), default=uuid.uuid4(), nullable=False)
    code = db.Column(db.String, primary_key=True)
    expires_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, invitee, code, expires_at):
        self.invitee = invitee
        self.code = code
        self.expires_at = expires_at

    def __repr__(self):
        return f'FriendInvite({self.invitee}, {self.code}, {self.expires_at})'

    # To DELETE a row from the table
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    # To SAVE a row from the table
    def save(self):
        db.session.add(self)
        db.session.commit()

class lang(enum.Enum):
    catalan = "catalan"
    spanish = "spanish"
    english = "english"

class UserLanguage(db.Model):
    __tablename__ = 'user_lang'

    user = db.Column(UUID(as_uuid=True), db.ForeignKey(User.id), primary_key=True, default=uuid.uuid4())
    language = db.Column(db.Enum(lang), primary_key=True)

    def __init__(self, user, language):
        self.user = user
        self.language = language

    def __repr__(self):
        return f'UserLanguage({self.user}, {self.language})'

    # To DELETE a row from the table
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    # To SAVE a row from the table
    def save(self):
        db.session.add(self)
        db.session.commit()

class BannedEmails(db.Model):
    __tablename__ = 'banned_emails'

    email = db.Column(db.String, primary_key=True)
    username = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.String)

    def __init__(self, email, username, date, reason):
        self.email = email
        self.username = username
        self.date = date
        self.reason = reason
    
    def __repr__(self):
        return f'BannedEmail({self.email}, {self.username}, {self.date}, {self.reason})'
    
    # To DELETE a row from the table
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    # To SAVE a row from the table
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    @staticmethod
    def exists(email):
        return BannedEmails.query.filter_by(email = email).first() != None