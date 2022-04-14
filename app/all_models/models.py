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
        return "".format(self.DateHour)

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

    def __init__(self, Name, Eoicode, StationType, UrbanArea, Height, GeoReference):
        """initialize with name."""
        self.Name = Name
        self.EOIcode = Eoicode
        self.StationType = StationType
        self.UrbanArea = UrbanArea
        self.Height = Height
        self.GeoReference = GeoReference

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return AirQualityStation.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "".format(self.Name, self.EOIcode, self.StationType, self.UrbanArea, self.Height, self.GeoReference)
class AirQualityData(db.Model):
    __tablename__ = 'AirQualityData'

    DateHour = db.Column(db.DateTime, db.ForeignKey("DateHour"), primary_key=True)
    EOIcodeStation = db.Column(db.Integer, db.ForeignKey("AirQualityStation"))
    
    Magnitude = db.Column(db.Integer)
    PollutantComposition = db.Column(db.String)
    Units = db.Column(db.String)

    def __init__(self, DateHour, EOIcodeStation, Magnitude, PollutantComposition, Units):
        """initialize with name."""
        self.DateHour = DateHour
        self.EOIcodeStation = EOIcodeStation
        self.Magnitude = Magnitude
        self.PollutantComposition = PollutantComposition
        self.Units = Units


    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return AirQualityData.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "".format(self.DateHour, self.EOIcode, self.Magnitude, self.PollutantComposition, self.Units)

class Language(db.Model):

    __tablename__ = 'Language'

    name = db.Column(db.String, primary_key=True)

    def __init__(self, name):
        self.name = name

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return AirQualityData.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "".format(self.name)

class LanguageUser(db.Model):
    __tablename__ = 'LanguageUser'

    Language = db.Column(db.String, db.ForeignKey("Language"), primary_key=True)
    #UserName = db.Column(db.String, db.ForeignKey("User"), primary_key=True)

    def __init__(self, Language):
        self.Language = Language

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return AirQualityData.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "".format(self.Language)

class SocialMedia(db.Model):
    __tablename__ = 'SocialMedia'

    name = db.Column(db.String, primary_key=True)

class SocialMediaUser(db.Model):
    __tablename__ = 'SocialMediaUser'

    SocialMediaName = db.Column(db.String, db.ForeignKey("SocialMedia"), primary_key=True)
    #UserName = db.Column(db.String, db.ForeignKey("User"), primary_key=True)

class Achievements(db.Model):
    __tablename__ = 'Achievements'

    ID = db.Column(db.String, primary_key=True)
    Name = db.Column(db.String)
    Requeriments = db.Column(db.String)