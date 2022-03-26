from app import db

class date_hour(db.Model):
    __tablename__ = 'date_hour'
    date_hour =db.Column(db.DateTime, default=db.func.current_timestamp() , primary_key=True)
    

    def __init__(self, date_hour):
        self.date_hour = date_hour

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return date_hour.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "".format(self.date_hour)

import enum 
class station_type(enum.Enum):
    traffic = "Traffic"
    background = "Background"
    industrial = "Industrial"

class urban_area(enum.Enum):
    urban = "Urban"
    periurban = "Peri-Urban"
    rural = "Rural"


class air_quality_station(db.Model):
    __tablename__ = 'air_quality_station'

    name = db.Column(db.String)
    eoi_code = db.Column(db.String, primary_key=True)
    station_type = db.Column(db.Enum(station_type))
    urbanArea = db.Column(db.Enum(urban_area))
    height = db.Column(db.Integer)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    air_condition_scale = db.Column(db.Float)
    time_computation_scale = db.Column(db.DateTime)
    #Ubicacion = db.Column(db.Integer, db.ForeignKey("Identificador")) 

    def __init__(self, name, eoi_code, station_type, urban_area, height, latitude, lenght, air_condition_scale, time_computation_scale):
        
        self.name = name
        self.eoi_code = eoi_code
        self.station_type = station_type
        self.urban_area = urban_area
        self.height = height
        self.latitude = latitude
        self.lenght = lenght
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
        return "".format(self.name, self.eoi_code, self.station_type, self.urban_area, self.height, self.latitude, self.lenght, self.air_condition_scale, self.time_computation_scale)

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

    date_hour = db.Column(db.DateTime, db.ForeignKey(date_hour.date_hour), primary_key=True)
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




