from urllib import response
import requests
import json


#llamadas a la API que contiene datos sobre la contaminación del aire
url = 'https://analisi.transparenciacatalunya.cat/resource/tasf-thgu.json?data=2022-03-20&nom_estacio=Gavà&$order=codi_eoi'
#url = 'https://analisi.transparenciacatalunya.cat/resource/tasf-thgu.json?data=2022-03-20&$order=codi_eoi'
#url = 'https://analisi.transparenciacatalunya.cat/resource/tasf-thgu.json?$select=distinct contaminant'
#url = 'https://analisi.transparenciacatalunya.cat/resource/tasf-thgu.json?$select=distinct tipus_estacio'
response = requests.get(url)
response_json = response.json()

#mostrar resultados
for d in response_json:
    
    for keys in d:
        print(keys, ':', d[keys])



codi_eoi=0; nom_estacio=''; contaminant=''; unitats=''; tipus_estacio=''; area_urbana='';magnitud = 0
h1=0; h2=0; h3=0; h4=0; h5=0; h6=0; h7=0; h8=0; h9=0; h10=0; h11=0; h12=0
h13=0; h14=0; h15=0; h16=0; h17=0; h18=0; h19=0; h20=0; h21=0; h22=0; h23=0; h24=0
altitud=''; latitud=''; longitud=''; resultado_final=0.0; 

primero = 1
codi_previ = ''
horas = {}
contaminantes={}

for d in response_json:

    codi_actual = d['codi_eoi']
    if primero:
        primero = 0
        codi_previ = codi_actual
        codi_eoi = codi_actual


    
    for key in d:
        if codi_actual != codi_previ:
            #-----------> Calculo de heuristica y envio a BD
            codi_eoi = codi_actual
            contaminantes.clear()

        else:
            if key == 'nom_estacio': nom_estacio = d[key]
            elif key == 'unitats': unitats = d[key]
            elif key == 'tipus_estacio': tipus_estacio = d[key]
            elif key == 'area_urbana': area_urbana = d[key]
            elif key == 'magnitud': magnitud = d[key]
            elif key == 'contaminant': contaminant = d[key]
            elif key == 'altitud': altitud = d[key]
            elif key == 'latitud': latitud = d[key]
            elif key == 'longitud': longitud = d[key]
            else:
                if key!='data' and key!='codi_ine' and key!='municipi' and key!='codi_comarca' and key!='nom_comarca' and key!='geocoded_column' and key!= 'codi_eoi': 
                    horas[key] = d[key]
    
    
    for elem in horas:
        resultado_final = resultado_final + float(horas[elem])

    if len(horas) > 0:
        resultado_final = resultado_final/len(horas)

    #print(d['contaminant'])
    contaminantes[d['contaminant']] = resultado_final 
    #print('resultado_final: ', resultado_final)

    h1=0; h2=0; h3=0; h4=0; h5=0; h6=0; h7=0; h8=0; h9=0; h10=0; h11=0; h12=0
    h13=0; h14=0; h15=0; h16=0; h17=0; h18=0; h19=0; h20=0; h21=0; h22=0; h23=0; h24=0
    resultado_final = 0.0
    horas.clear()


    codi_previ = codi_actual





#AirQualityStation.__init__()


#calculo de heuristica para determinar la calidad final del aire
def heuristica_contaminantes():
    
    print()

