import os
from sqlalchemy import create_engine

# Import pickle library to save python objects to file
import pickle as pkl

#FIXME: Change MIGRATIONS_ to URI in production. Now it is needed for testing from console.
engine = create_engine(os.getenv("MIGRATIONS_SQLALCHEMY_DATABASE_URI"))


#Cada clave es el ID del contaminante
#Sus valores [valor maxumo, peso]
contaminantes = {
    'C6H6':[68,0.135],
    'Cl2':[35,0.135],
    'CO':[21,0.135],
    'H2S':[650,0.043],
    'HCl':[182,0.043],
    'HCNM':[50,0.135],
    'HCT':[50,0.135],
    'NO2':[1000,0.005],
    'O3':[300,0.043],
    'PM2.5':[153,0.042],
    'PM10':[258,0.043],
    'PM1':[130,0.043],
    'PS':[1500,0.005],
    'SO2':[1355,0.005],
    'Hg':[707,0.043],
    'NO':[1230,0.005],
    'NOX':[1138,0.005]
}


def insert_pollutant_data(contaminantes: dict) -> None:
    for key in contaminantes:
        compos = key
        lower = 0.0
        upper = contaminantes[key][0]
        unidades = 'µg/m3'
        peso = contaminantes[key][1]
        with engine.connect() as conn:
            conn.execute(
                'INSERT INTO pollutant VALUES(%s,%s,%s,%s,%s)',
                (compos, lower, upper, unidades, peso)
            )



