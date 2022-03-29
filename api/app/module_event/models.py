# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from app import db
from sqlalchemy.dialects.postgresql import UUID
import uuid


# Define an Event model
class Event(db.Model):

    __tablename__ = 'events'

    # Event id
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    # Event name
    name = db.Column(db.String, nullable=False)
    # Event description
    description = db.Column(db.String, nullable=False)
    # Start date of the event
    date_started = db.Column(db.DateTime, nullable=False)
    # End date of the event
    date_end = db.Column(db.DateTime, nullable=False)
    # Creator of the event
    user_creator = db.Column(UUID(as_uuid=True), nullable=False)
    # Longitude of the location where the event will take taking place
    longitud = db.Column(db.Float, nullable=False)
    # Latitude of the location where the event will take taking place
    latitude = db.Column(db.Float, nullable=False)
    # Number of max participants of the event
    max_participants = db.Column(db.Integer, nullable=False)

    # To CREATE an instance of an Event
    def __init__(self, id, name, description, date_started, date_end, user_creator, longitud, latitude, max_participants):

        self.id = id
        self.name = name
        self.description = description
        self.date_started = date_started
        self.date_end = date_end
        self.user_creator = user_creator
        self.longitud = longitud
        self.latitude = latitude
        self.max_participants = max_participants

    # To FORMAT an Event in a readable string format 
    def __repr__(self):
        return 'Event(id: ' + str(self.id) + ', name: ' + str(self.name) + ', description: ' + str(self.description) + ', date_started: ' + str(self.date_started) + ', date_end: ' + str(self.date_end) + ', user_creator: ' + str(self.user_creator) + ', longitud: ' + str(self.longitud) + ', latitude: ' + str(self.latitude) + ', max_participants: ' + str(self.max_participants) + ').'

    # To DELETE a row from the table
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    # To SAVE a row from the table
    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    # To GET ALL ROWS of the table
    def get_all():
        return Event.query.all()

    # To CONVERT an Event object to a dictionary
    def toJSON(self):
        eventJSON = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "date_started": self.date_started,
            "date_end": self.date_end,
            "user_creator": self.user_creator,
            "longitud": self.longitud,
            "latitude": self.latitude,
            "max_participants": self.max_participants
        }
        return eventJSON