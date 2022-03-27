from urllib import response
from datetime import datetime
from datetime import timedelta
import requests
import json
import os

from app.module_airservice.jobs.pollutants import contaminantes
from sqlalchemy import create_engine

from app.module_airservice.models import station_type, urban_area

#FIXME: Change MIGRATIONS_ to URI in production. Now it is needed for testing from console.
engine = create_engine(os.getenv("MIGRATIONS_SQLALCHEMY_DATABASE_URI"))


hours = ['h01','h02','h03','h04','h05','h06',
         'h07','h08','h09','h10','h11','h12',
         'h13','h14','h15','h16','h17','h18',
         'h19','h20','h21','h22','h23','h24']


date_today = datetime.today()
date_anterior = date_today - timedelta(days = 1)
date_anterior = date_anterior.strftime('%Y-%m-%d')



def insert_air_station(eoi_code, name, station_t, urban_a, altitude, latitude, longitude) -> None:
    try:
        with engine.connect() as conn:
            conn.execute(
                'INSERT INTO air_quality_station VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                (eoi_code, name, station_t, urban_a, altitude, latitude, longitude, 0.0, data_today)
            )
    except Exception as err:
        print("Falla inserir estacion")
        print(err)


def normalizar(cont, valor) -> float:
        return round(valor/contaminantes[cont][0],2)


def insert_hour_data(hour, codi_eoi, value, pollutant) -> None:
        hour_2 = hour[-2:] #obtener los dos ultimos caracteres
        date_hora_final = date_anterior+' '+hour_2+':00:00'
        if hour_2 == 24: date_hora_final = date_today.strftime('%Y-%m-%d')+' 00:00:00:000000'
        #date_time_obj = datetime.strptime(date_hora_final, '%Y-%m-%d %H:%M:%S')
        cont_scale = normalizar(pollutant,value)
        try:
            with engine.connect() as conn:
                conn.execute(
                  'INSERT INTO air_quality_data VALUES(%s,%s,%s,%s,%s)',
                   (date_hora_final, codi_eoi, pollutant, value, cont_scale)
                )
        except Exception as err:
                with engine.connect() as conn:
                    res = conn.execute(
                        'SELECT * FROM air_quality_data WHERE date_hour = %s and station_eoi_code = %s and pollutant_composition = %s;',
                        (date_hora_final, codi_eoi, pollutant)
                    ).fetchall()
                print(res)
                print("Falla inserir medida")
                print(err)
                exit()
            

if __name__ == '__main__':
    
    url = f"https://analisi.transparenciacatalunya.cat/resource/tasf-thgu.json?data={date_anterior}&nom_estacio=Gavà&$order=codi_eoi"

    #llamada a la API que contiene datos sobre la contaminación del aire del dia
    response = requests.get(url)
    response_json = response.json()

    contaminantes_json = [ j['contaminant'] for j in response_json ]

    with engine.connect() as conn:
        all_eoi_codes = conn.execute('SELECT DISTINCT eoi_code FROM air_quality_station').fetchall()
    estaciones_vistas = set(map(lambda r: r[0], all_eoi_codes))

    for medicion in response_json:
        if medicion['codi_eoi'] not in estaciones_vistas:
            # Insertar estación
            insert_air_station (
                medicion['codi_eoi'],
                medicion['nom_estacio'],
                station_type[medicion['tipus_estacio']].value,
                urban_area[medicion['area_urbana']].value,
                int(medicion['altitud']),
                float(medicion['latitud']),
                float(medicion['longitud'])
            )
            estaciones_vistas.add(medicion['codi_eoi'])
        
        # Insertar medición
        for hour in hours:
            #no todas las horas existen
            if medicion[hour] in medicion:
                #insertar hora
                insert_hour_data(
                    hour,
                    medicion['codi_eoi'],
                    medicion['contaminant'],
                    medicion[hour]
                    )
 
    print(contaminantes_json)
    exit()




   

