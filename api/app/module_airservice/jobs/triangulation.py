# Import db connection library
import os
from sqlalchemy import create_engine

# Import triangulations library
import matplotlib.tri as mtri

# Import time libraries
from datetime import datetime, timedelta

# Import pickle library to save python objects to file
import pickle as pkl

triangulation_file_path = 'triangulation.pkl'
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
        # 1st approach: take average -> next apply ponderation following heuristic
        air_data = conn.execute(
            'SELECT aqs.eoi_code, aqs.lon, aqs.lat, avg(aqd.quality) \
            FROM air_quality_data aqd inner join air_quality_station aqs on aqd.eoi_code = aqs.eoi_code \
            WHERE aqd.date_hour = %s \
            GROUP BY aqd.eoi_code, aqs.lon, aqs.lat;',
            (qstring)
        ).fetchall()
    
    print(air_data)
    return air_data

def update_station_general_quality(air_data) -> None:
    for entry in air_data:
        eoi_code = entry[0]
        general_quality = entry[3]
        with engine.connect() as conn:
            conn.execute(
                'UPDATE air_quality_station \
                SET last_quality = %s \
                WHERE eoi_code = %s;',
                (general_quality, eoi_code)
            )

def triangulate(air_data) -> mtri.Triangulation:
    # create numpy arrays for triangulation
    # Testing triangulation
    #x = [1,4,2,0,3,2,5,1,3]
    #y = [4,4,3,2,2,1,1,0,0]
    x = list(map(lambda x: x[1], air_data))
    y = list(map(lambda x: x[2], air_data))
    return mtri.Triangulation(x,y)

def save_current_triangulation(triangulation, air_data) -> None:
    with open(triangulation_file_path, 'w') as out:
        pkl.dump({'tri':triangulation, 'idx_data': air_data}, out, pkl.HIGHEST_PROTOCOL)

def generate_heat_map() -> None:
    print("not implemented")
    # Use some python image generation software with the triangles of the 
    #  Triangulation and quality mapped to colors (from a range)
    #  as color values of vertices

if __name__ == '__main__':
    #air_data = fetch_air_data()
    #update_station_general_quality(air_data)
    #triangulation = triangulate(air_data)
    #save_current_triangulation(triangulation, air_data)

    print('main')
    # run script every hour
    triangulation = triangulate([(-1,0,0,-1),(-1,1,1,-1),(-1,0,2,-1),(-1,1,-1,-1)])
    trifinder = triangulation.get_trifinder()
    print(triangulation.triangles)
    print(trifinder([.5],[0.4]))
    exit()
    dt = datetime(year=2022, month=1, day=1, hour = 3) - timedelta(days=1)
    print(dt.year)
    print(dt.month)
    print(dt.day)
    print(dt.hour)
    print(dt.minute)

    print(DateTime().python_type(year=2022, month=3, day=24))
