# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from app import db

# Define a User model
class DateAndTime(db.Model):

    __tablename__ = 'events'

    # Date and time id
    dateAndTime = db.Column(db.DateTime, primary_key=True)

    # New instance instantiation procedure
    def __init__(self, dateAndTime):

        self.dateAndTime = dateAndTime

    def __repr__(self):
        return '<Event %r>' % (self.name)
