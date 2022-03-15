# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from app import db
from uuid import UUID

# Define a User model
class User(db.Model):

    __tablename__ = 'events'

    # User id
    id = db.Column(UUID(as_uuid=true), primary_key=True, default=uuid.uuid4)
    # Event name
    name = db.Column(db.String)
    # Event description
    description = db.Column(db.String)

    # New instance instantiation procedure
    def __init__(self, id, name, description):

        self.id = id
        self.name = name
        self.description = description

    def __repr__(self):
        return '<Event %r>' % (self.name)
