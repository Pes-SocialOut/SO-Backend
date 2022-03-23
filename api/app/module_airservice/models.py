from app import db

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

    DateHour = db.Column(db.DateTime, db.ForeignKey(DateHour.DateHour), primary_key=True)
    EOIcodeStation = db.Column(db.String, db.ForeignKey(AirQualityStation.EOIcode), primary_key=True)
    
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
