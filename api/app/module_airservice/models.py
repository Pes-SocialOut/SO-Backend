from app import db
import enum
from sqlalchemy.dialects.postgresql import BYTEA

class station_type(enum.Enum):
    traffic = "traffic"
    background = "background"
    industrial = "industrial"

class urban_area(enum.Enum):
    urban = "urban"
    periurban = "peri-urban"
    suburban = "suburban"
    rural = "rural"

class air_quality_station(db.Model):
    __tablename__ = 'air_quality_station'

    name = db.Column(db.String)
    eoi_code = db.Column(db.String, primary_key=True)
    station_type = db.Column(db.Enum(station_type))
    urban_area = db.Column(db.Enum(urban_area))
    altitude = db.Column(db.Integer)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    air_condition_scale = db.Column(db.Float)
    time_computation_scale = db.Column(db.DateTime)

    def __init__(self, name, eoi_code, station_type, urban_area, altitude, latitude, longitude, air_condition_scale, time_computation_scale):
        
        self.name = name
        self.eoi_code = eoi_code
        self.station_type = station_type
        self.urban_area = urban_area
        self.altitude = altitude
        self.latitude = latitude
        self.longitude = longitude
        self.air_condition_scale = air_condition_scale
        self.time_computation_scale = time_computation_scale

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return air_quality_station.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "".format(self.name, self.eoi_code, self.station_type, self.urban_area, self.altitude, self.longitude, self.latitude, self.air_condition_scale, self.time_computation_scale)

    def toJSON(self):
        return {
            'eoi_code': self.eoi_code,
            'name': self.name,
            'station_type': self.station_type.value,
            'urban_area': self.urban_area.value,
            'altitude': self.altitude,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'pollution': self.air_condition_scale,
            'last_calculated_at': self.time_computation_scale
        }

class pollutant(db.Model):
    __tablename__ = 'pollutant'
    composition = db.Column(db.String, primary_key=True)
    common_lowerbound = db.Column(db.Float)
    common_upperbound = db.Column(db.Float)
    units = db.Column(db.String)
    air_quality_weight = db.Column(db.Float)

    def __init__(self, composition, common_lowerbound, common_upperbound, units, air_quality_weight):
        
        self.composition = composition
        self.common_lowerbound = common_lowerbound
        self.common_upperbound = common_upperbound
        self.units = units
        self.air_quality_weight = air_quality_weight

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return air_quality_station.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "".format(self.composition, self.common_lowerbound, self.common_upperbound, self.units, self.air_quality_weight)

class air_quality_data(db.Model):
    __tablename__ = 'air_quality_data'

    date_hour = db.Column(db.DateTime, primary_key=True)
    station_eoi_code = db.Column(db.String, db.ForeignKey(air_quality_station.eoi_code), primary_key=True)
    pollutant_composition = db.Column(db.String, db.ForeignKey(pollutant.composition), primary_key=True)
    value = db.Column(db.Float)
    contaminant_scale = db.Column(db.Float)
   
    def __init__(self, date_hour, station_eoi_code, pollutant_composition, value, contaminant_scale):
       
        self.date_hour = date_hour
        self.station_eoi_code = station_eoi_code
        self.pollutant_composition = pollutant_composition
        self.value = value
        self.contaminant_scale = contaminant_scale

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return air_quality_data.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "".format(self.date_hour, self.station_eoi_code, self.pollutant_composition, self.value, self.contaminant_scale)

    def toJSON(self):
        return {
            'date_hour': self.date_hour,
            'station_eoi_code': self.station_eoi_code,
            'pollutant_composition': self.pollutant_composition,
            'value': self.value,
            'contaminant_scale': self.contaminant_scale
        }

class triangulation_cache(db.Model):
    __tablename__ = 'tri_cache'

    date_hour = db.Column(db.DateTime, primary_key=True)
    tri_object_bytes = db.Column(BYTEA)

    def __init__(self):
        self.tri_object_bytes = None
