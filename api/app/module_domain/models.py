# app/models.py

from app import db


class Template(db.Model):
    """This class represents the bucketlist table."""

    __tablename__ = 'template'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())
    foreign_keys = db.Column(db.Integer, db.ForeignKey("nombreDatabase"))
    

    def __init__(self, name):
        """initialize with name."""
        self.name = name

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Template.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "".format(self.name)


class DateHour(db.Model):
    __tablename__ = 'DateHour'
    DateHour =db.Column(db.DateTime, default=db.func.current_timestamp() , primary_key=True)
    

    def __init__(self, DateHour):
        """initialize with name."""
        self.DateHour = DateHour

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return DateHour.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "".format(self.name)

import enum 
class StationType(enum.Enum):
    TRAFFIC = "Traffic"
    BACKGROUND = "Background"
    INDUSTRIAL = "Industrial"

class UrbanArea(enum.Enum):
    URBAN = "Urban"
    PERIURBAN = "Peri-Urban"
    RURAL = "Rural"




class AirQualityStation(db.Model):
    __tablename__ = 'AirQualityStation'

    Name = db.Column(db.String)
    EOIcode = db.Column(db.String, primary_key=True)
    StationType = db.Column(db.Enum(StationType))
    UrbanArea = db.Column(db.Enum(UrbanArea))
    Height = db.Column(db.Integer)
    GeoReference = db.Column(db.String)
    #Ubicacion = db.Column(db.Integer, db.ForeignKey("Identificador")) 


class Language(db.Model):

    __tablename__ = 'Language'

    name = db.Column(db.String, primary_key=True)

class LanguageUser(db.Model):
    __tablename__ = 'LanguageUser'

    Language = db.Column(db.String, db.ForeignKey("Language"), primary_key=True)
    UserName = db.Column(db.String, db.ForeignKey("User"), primary_key=True)

class SocialMedia(db.Model):
    __tablename__ = 'SocialMedia'

    name = db.Column(db.String, primary_key=True)

class SocialMediaUser(db.Model):
    __tablename__ = 'SocialMediaUser'

    SocialMediaName = db.Column(db.String, db.ForeignKey("SocialMedia"), primary_key=True)
    UserName = db.Column(db.String, db.ForeignKey("User"), primary_key=True)

class Logros(db.Model):
    __tablename__ = 'Logros'

    ID = db.Column(db.String, primary_key=True)
    Name = db.Column(db.String)
    Requeriments = db.Column(db.String)