from app import db
from sqlalchemy.dialects.postgresql import UUID
import uuid

# Define a User model
class User(db.Model):
    __tablename__ = 'users'

    # User id
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    # Username
    username = db.Column(db.String, nullable=False)
    # Email
    email = db.Column(db.String, unique=True, nullable=False)
    # URL of the full-resolution profile image
    profile_img_uri = db.Column(db.String)
    # URL of the reduced-resolution profile image
    mini_profile_img_uri = db.Column(db.String)
    # User description / information
    description = db.Column(db.String, default="", nullable=False)
    # User hobbies
    hobbies = db.Column(db.String, default="", nullable=False)

    # To CREATE an instance of a User
    def __init__(self, id, username, email, profile_img_uri, mini_profile_img_uri, description, hobbies):
        self.id = id
        self.username = username
        self.email = email
        self.profile_img_uri = profile_img_uri
        self.mini_profile_img_uri = mini_profile_img_uri
        self.description = description
        self.hobbies = hobbies

    def __repr__(self):
        return f'User({self.id}, {self.username}, {self.profile_img_uri}, {self.mini_profile_img_uri}, {self.description}, {self.hobbies})'

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
            'profile_img_uri': self.profile_img_uri,
            'mini_profile_img_uri': self.mini_profile_img_uri,
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

    def __init__(self, email, code):
        self.email = email
        self.code = code

    def __repr__(self):
        return f'User({self.email}, {self.code})'

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
