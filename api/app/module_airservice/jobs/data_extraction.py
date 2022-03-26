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


codi_eoi=''; nom_estacio=''; contaminant=''; unitats=''
tipus_estacio=''; area_urbana='';magnitud = 0
altitud=''; latitud=0.0; longitud=0.0; geocoded=''


data_today = datetime.today()
data_anterior = data_today - timedelta(days = 1)
data_anterior = data_anterior.strftime('%Y-%m-%d')



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
        return valor/contaminantes[cont][0]


def insert_hours_data(horas: dict, hora_real) -> None:
        date_time_str = data_anterior
        date_hora_final = ''
        for key in horas:
            hr = key[-2:]
            date_hora_final = date_time_str+' '+hr+':00:00'
            if hr == 24: date_hora_final = data_today.strftime('%Y-%m-%d')+' 00:00:00'
            #date_time_obj = datetime.strptime(date_hora_final, '%Y-%m-%d %H:%M:%S')
            cont_scale = normalizar(contaminant,horas[key])
            try:
                with engine.connect() as conn:
                    conn.execute(
                        'INSERT INTO air_quality_data VALUES(%s,%s,%s,%s,%s)',
                        (date_hora_final,codi_eoi,contaminant,horas[key],cont_scale)
                    )
            except Exception as err:
                with engine.connect() as conn:
                    res = conn.execute(
                        'SELECT * FROM air_quality_data WHERE date_hour = %s and station_eoi_code = %s and pollutant_composition = %s;',
                        (date_hora_final,codi_eoi,contaminant)
                    ).fetchall()
                print(res)
                print("Falla inserir medida")
                print(err)
                exit()
            

if __name__ == '__main__':
    
    url = f"https://analisi.transparenciacatalunya.cat/resource/tasf-thgu.json?data={data_anterior}&nom_estacio=Gavà&$order=codi_eoi"

    #llamada a la API que contiene datos sobre la contaminación del aire del dia
    response = requests.get(url)
    response_json = response.json()

    contaminantes_json = [ j['contaminant'] for j in response_json ]

    with engine.connect() as conn:
        all_eoi_codes = conn.execute('SELECT eoi_code FROM air_quality_station').fetchall()
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


    print(contaminantes_json)
    exit()

    primero1 = 1
    primero2 = 1
    codi_previ = ''
    horas = {}

    for d in response_json:

        codi_actual = d['codi_eoi']
        if primero1:
            primero1 = 0
            codi_previ = codi_actual
            codi_eoi = codi_actual


        for key in d:
            if codi_actual != codi_previ:
                codi_eoi = codi_actual

            else:
                if key == 'nom_estacio': nom_estacio = d[key]
                elif key == 'unitats': unitats = d[key]
                elif key == 'tipus_estacio': tipus_estacio = station_type[d[key]].value
                elif key == 'area_urbana': area_urbana = urban_area[d[key]].value
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




   

