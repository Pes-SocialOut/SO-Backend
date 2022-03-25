# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from app import db
from sqlalchemy.dialects.postgresql import UUID
import uuid


# Define a User model
class Event(db.Model):

    __tablename__ = 'events'

    # Event id
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    # Event name
    name = db.Column(db.String, nullable=False)
    # Event description
    description = db.Column(db.String, nullable=False)
    # Start date of the event
    dateStarted = db.Column(db.DateTime, nullable=False)
    # End date of the event
    dateEnd = db.Column(db.DateTime, nullable=False)
    # Creator of the event
    userCreator = db.Column(UUID(as_uuid=True), nullable=False)
    # Longitude of the location where the event will take taking place
    longitud = db.Column(db.Float, nullable=False)
    # Latitude of the location where the event will take taking place
    latitude = db.Column(db.Float, nullable=False)

    # New instance instantiation procedure
    def __init__(self, id, name, description, dateCreated, dateEnd, userCreator, longitud, latitude):

        self.id = id
        self.name = name
        self.description = description
        self.dateCreated = dateCreated
        self.dateEnd = dateEnd
        self.userCreator = userCreator
        self.longitud = longitud
        self.latitude = latitude

    def __repr__(self):
        return '<Event %r>' % (self.name)
