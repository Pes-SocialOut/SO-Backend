# Import the database object from the main app module
from app import db

# Import module models
from app.module_airservice.models import AirQualityData, AirQualityStation

# Import triangulations library
import matplotlib.tri as mtri
import numpy as np

def fetch_air_data() -> None:
    print('not implemented')
    print(AirQualityData.query.filter_by(DateHour='2022-03-21').order_by(AirQualityData.EOIcodeStation.desc()).all())
    # Get all AirQualityStations from measurments 24h ago
    # for each AirQualityStation:
        # Get all measurements of airstation+date(24h ago).
        # Calculate a ponderated weight "quality" from the measurements
        # Add airstation + quality to datastructure

def triangulate() -> mtri.Triangulation:
    print("not implemented")
    # create numpy arrays for triangulation
    # return mtri.triangulate(x,y)

def save_current_triangulation() -> None:
    print("not implemented")
    # save pkl with datastructure and Triangulation
        #(to be read by endpoint air/point when interpolating the aprox. value)

def generate_heat_map() -> None:
    print("not implemented")
    # Use some python image generation software with the triangles of the 
    #  Triangulation and quality mapped to colors (from a range)
    #  as color values of vertices

if __name__ == '__main__':
    print('main')
    # run script every hour
