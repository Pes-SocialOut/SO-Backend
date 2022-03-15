# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from app import db
from uuid import UUID

# Define a User model
class Event(db.Model):

    __tablename__ = 'events'

    # Event id
    id = db.Column(UUID(as_uuid=true), primary_key=True, default=uuid.uuid4)
    # Event name
    name = db.Column(db.String)
    # Event description
    description = db.Column(db.String)
    # Start date of the event
    dateStarted = db.Column(db.DateTime)
    # End date of the event
    dateEnd = db.Column(db.DateTime)
    # Creator of the event
    userCreator = db.Column(UUID(as_uuid=true))
    # Longitude of the location where the event will take taking place
    longitud = db.Column(db.Float)
    # Latitude of the location where the event will take taking place
    latitude = db.Column(db.Float)

    # New instance instantiation procedure
    def __init__(self, id, name, description, dateCreated, dateEnd, userCreator):

        self.id = id
        self.name = name
        self.description = description
        self.dateCreated = dateCreated
        self.dateEnd = dateEnd
        self.userCreator = userCreator

    def __repr__(self):
        return '<Event %r>' % (self.name)
