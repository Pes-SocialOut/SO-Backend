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
    description = db.Column(db.String, default="")

    # To CREATE an instance of a User
    def __init__(self, id, username, email, profile_img_uri, mini_profile_img_uri, description):
        self.id = id
        self.username = username
        self.email = email
        self.profile_img_uri = profile_img_uri
        self.mini_profile_img_uri = mini_profile_img_uri
        self.description = description

    def __repr__(self):
        return f'User({self.id}, {self.username}, {self.profile_img_uri}, {self.mini_profile_img_uri}, {self.description})'

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
            'profile_img_uri': self.profile_img_uri.value,
            'mini_profile_img_uri': self.mini_profile_img_uri,
            'description': self.description
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

class GoogleAuth(db.Model):
    __tablename__ = 'google_auth'

    # User id
    id = db.Column(UUID(as_uuid=True), db.ForeignKey(User.id), primary_key=True, default=uuid.uuid4())
    # Google id
    google_id = db.Column(db.String, unique=True, nullable=False)
    # Google access token
    access_token = db.Column(db.String, nullable=False)

    # To CREATE an instance of a GoogleUser
    def __init__(self, id, google_id, access_token):
        self.id = id
        self.google_id = google_id
        self.access_token = access_token

    def __repr__(self):
        return f'User({self.id}, {self.google_id}, {self.access_token})'

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
    # facebook id
    facebook_id = db.Column(db.String, unique=True, nullable=False)
    # facebook access token
    access_token = db.Column(db.String, nullable=False)

    # To CREATE an instance of a facebookUser
    def __init__(self, id, facebook_id, access_token):
        self.id = id
        self.facebook_id = facebook_id
        self.access_token = access_token

    def __repr__(self):
        return f'User({self.id}, {self.facebook_id}, {self.access_token})'

    # To DELETE a row from the table
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    # To SAVE a row from the table
    def save(self):
        db.session.add(self)
        db.session.commit()