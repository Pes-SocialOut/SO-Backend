# Import db connection library
import os
from sqlalchemy import create_engine

# Import triangulations library
import matplotlib.tri as mtri
import math

# Import time libraries
from datetime import datetime, timedelta

# Import pickle library to save python objects to file
import pickle as pkl

triangulation_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','triangulation.pkl')

#FIXME: Change MIGRATIONS_ to URI in production. Now it is needed for testing from console.
engine = create_engine(os.getenv("MIGRATIONS_SQLALCHEMY_DATABASE_URI"))

def fetch_air_data() -> list:
    yesterday = datetime.now() - timedelta(days = 1)
    if yesterday.minute > 30:
        yesterday += timedelta(hours = 1)
    qyear = yesterday.year
    qmonth = yesterday.month
    qday = yesterday.day
    qhour = yesterday.hour
    qstring = f'{qyear}-{qmonth}-{qday} {qhour}:00:00'

    with engine.connect() as conn:
        air_data = conn.execute(
            'SELECT aqs.eoi_code, aqs.longitude, aqs.latitude, sum( aqd.contaminant_scale*p.air_quality_weight ) / sum(p.air_quality_weight) \
            FROM air_quality_data aqd inner join air_quality_station aqs on aqd.station_eoi_code = aqs.eoi_code \
                inner join pollutant p on aqd.pollutant_composition = p.composition \
            WHERE aqd.date_hour = %s \
            GROUP BY aqs.eoi_code, aqs.longitude, aqs.latitude;',
            (qstring)
        ).fetchall()

    return air_data

def update_station_general_quality(air_data: list) -> None:
    upd_time = datetime.now()
    for entry in air_data:
        eoi_code = entry[0]
        general_quality = entry[3]
        with engine.connect() as conn:
            conn.execute(
                'UPDATE air_quality_station \
                SET air_condition_scale = %s, time_computation_scale = %s \
                WHERE eoi_code = %s;',
                (general_quality, upd_time, eoi_code)
            )

def add_map_bounding_vertices(air_data: list) -> list:
    # Add five arbitrary points that encapsulate all other points
    # and cover all of Catalunya's surface area.
    return [
        (None,  3.91, 42.394, -1),
        (None, 1.798, 43.136, -1),
        (None, -.477, 42.597, -1),
        (None, -.345, 40.023, -1),
        (None, 2.678, 40.659, -1),
    ] + air_data

def triangulate(air_data: list) -> mtri.Triangulation:
    # create arrays for triangulation
    x = list(map(lambda x: x[1], air_data))
    y = list(map(lambda x: x[2], air_data))
    return mtri.Triangulation(x,y)

def calculate_weighted_means_at_bounds(air_data: list, triangles: list) -> list:
    # For each bounding vertex
    for bnd_vtx in range(5):
        # Build list of adjacent vertices
        adjacencies = { idx for tri in triangles for idx in tri if bnd_vtx in tri }
        # Filter out all binding vertices
        adjacencies = list(filter(lambda x: x > 4, adjacencies))
        if len(adjacencies) == 0:
            continue
        # Assign a weighted quality guided by the distance to each neighbor
        v_lng = air_data[bnd_vtx][1]
        v_lat = air_data[bnd_vtx][2]
        distance = lambda lng, lat: math.sqrt((lng-v_lng)*(lng-v_lng) + (lat-v_lat)*(lat-v_lat))
        adj_distances = [distance(air_data[a][1], air_data[a][2]) for a in adjacencies]
        adj_weights = [1/dist for dist in adj_distances]
        adj_qualities = [air_data[a][3] for a in adjacencies]
        weighted_qualities = [adj_qualities[i]*adj_weights[i] for i in range(len(adjacencies))]
        v_quality = sum(weighted_qualities)/sum(adj_weights)

        air_data[bnd_vtx] = (None, v_lng, v_lat, v_quality)

    return air_data

def save_current_triangulation(triangulation, air_data) -> None:
    with open(triangulation_file_path, 'wb') as out:
        pkl.dump({'tri':triangulation, 'air': air_data}, out, pkl.HIGHEST_PROTOCOL)

def generate_heat_map() -> None:
    print("not implemented")
    # Use some python image generation software with the triangles of the 
    #  Triangulation and quality mapped to colors (from a range)
    #  as color values of vertices

if __name__ == '__main__':
    air_data = fetch_air_data()
    update_station_general_quality(air_data)
    air_data = add_map_bounding_vertices(air_data)
    triangulation = triangulate(air_data)
    air_data = calculate_weighted_means_at_bounds(air_data, triangulation.triangles)
    save_current_triangulation(triangulation, air_data)