from functions_calendar import crearEvento, editarEventoTitle, eliminarEventoID, buscarEventoTitle, eliminarEventoTitle, obtenerLocation

def main():

  # eliminarEvento('vl9q3r301tl29sg94gtpkq2f6c_20220511T070000Z') #funciona
  #buscarEventoTitle(stringtoken, 'Pruebitax2 Dia')
  #eliminarEventoTitle('Pruebitax2 Dia')
  crearEvento("ya29.a0ARrdaM99ZqlnV7u_IYRkbA6QjYmK7I8AbMNud4-GJRQQnFY-O8flULYrHh7hzxD-y84qewstJv3rzkiY16mvqdjSwAP4RUOO5wi9Yrvu4Asos0amdgn7j20lse0YYxfcmRZbi-0vy5kfT24_yDU7p1c2OpSq2Q", "maybe va ;)", "esto es un evento de prueba", 41.3713, 2.1494, '2022-05-10T09:00:00','2022-05-10T10:00:00')
  #obtenerLocation(41.3713, 2.1494)
  #editarEventoTitle("maybe va ;)","Ya las visto")

if __name__ == '__main__':
   main()

