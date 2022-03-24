# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from app import db
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid

# Define a User model
class User(db.Model):

    __tablename__ = 'events'

    # User id
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    # Username
    name = db.Column(db.String)

    # New instance instantiation procedure
    def __init__(self, id, name):
        self.id = id
        self.name = name


    def __repr__(self):
        return '<Event %r>' % (self.name)
