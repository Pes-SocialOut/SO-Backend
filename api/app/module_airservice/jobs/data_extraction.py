from typing_extensions import Self
from urllib import response
from datetime import datetime
from datetime import timedelta
import requests
import json
import os

from api.app.module_airservice.jobs.pollutants import contaminantes
from sqlalchemy import create_engine

from api.app.module_airservice.models import station_type, urban_area

# Import the database object from the main app module
#from app import db

# Import module models
#from app.module_airservice.models import AirQualityData, AirQualityStation

#FIXME: Change MIGRATIONS_ to URI in production. Now it is needed for testing from console.
engine = create_engine(os.getenv("MIGRATIONS_SQLALCHEMY_DATABASE_URI"))


codi_eoi=''; nom_estacio=''; contaminant=''; unitats=''
tipus_estacio=''; area_urbana='';magnitud = 0
altitud=''; latitud=0.0; longitud=0.0; geocoded=''


data_today = datetime.today()
data_anterior = data_today - timedelta(days = 1)
data_anterior = data_anterior.strftime('%Y-%m-%d')



def insert_air_station() -> None:
    airCS = 0.0
    try:
        with engine.connect() as conn:
            conn.execute(
                'INSERT INTO air_quality_station VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                (nom_estacio, codi_eoi, tipus_estacio, area_urbana, altitud, latitud, longitud, airCS, data_today)
            )
    except:
        pass


def normalizar(cont, valor) -> float:
        return valor/contaminantes[cont][0]


def insert_hours_data(horas: dict, hora_real) -> None:
        date_time_str = data_anterior
        date_hora_final = ''
        for key in horas:
            hr = key[-2:]
            date_hora_final = date_time_str+' '+hr+':00:00.000000'
            if hr == 24: date_hora_final = data_today.strftime('%Y-%m-%d')+' 00:00:00.000000'
            date_time_obj = datetime.strptime(date_hora_final, '%y-%m-%d %H:%M:%S')
            cont_scale = normalizar(contaminant,horas[key])
            try:
                with engine.connect() as conn:
                    conn.execute(
                        'INSERT INTO air_quality_data VALUES(%s,%s,%s,%s,%s)',
                        (date_time_obj,codi_eoi,contaminant,horas[key],cont_scale)
                    )
            except:
                print("insercion de horas va mal")
            

if __name__ == '__main__':

    url_aux1='https://analisi.transparenciacatalunya.cat/resource/tasf-thgu.json?data='
    url_aux2='&nom_estacio=Gavà&$order=codi_eoi'
    url = url_aux1+str(data_anterior)+url_aux2

    #llamada a la API que contiene datos sobre la contaminación del aire del dia
    response = requests.get(url)
    response_json = response.json()



    primero1 = 1
    primero2 = 1
    codi_previ = ''
    horas = {}

    for d in response_json:

        codi_actual = d['codi_eoi']
        if primero:
            primero = 0
            codi_previ = codi_actual
            codi_eoi = codi_actual


        for key in d:
            if codi_actual != codi_previ:
                codi_eoi = codi_actual

            else:
                if key == 'nom_estacio': nom_estacio = d[key]
                elif key == 'unitats': unitats = d[key]
                elif key == 'tipus_estacio': tipus_estacio = station_type[d[key]]
                elif key == 'area_urbana': area_urbana = urban_area[d[key]]
                elif key == 'magnitud': magnitud = d[key]
                elif key == 'contaminant': contaminant = d[key]
                elif key == 'altitud': altitud = int(d[key])
                elif key == 'latitud': latitud = float(d[key])
                elif key == 'longitud': longitud = float(d[key])
                else:
                    if key!='data' and key!='codi_ine' and key!='municipi' and key!='codi_comarca' and key!='nom_comarca' and key!='geocoded_column' and key!= 'codi_eoi': 
                        horas[key] = float(d[key])
        
        if primero2:
            primero2 = 0
            insert_air_station()
        
        if codi_actual != codi_previ :
            insert_air_station()


        for elem in horas:
            insert_hours_data(horas,elem) 
    
        codi_previ = codi_actual




   

