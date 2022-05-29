from functions_calendar import crearEvento, editarEventoTitle, eliminarEventoID, buscarEventoTitle, eliminarEventoTitle, obtenerLocation

def main():

  # eliminarEvento('vl9q3r301tl29sg94gtpkq2f6c_20220511T070000Z') #funciona
  #buscarEventoTitle(stringtoken, 'Pruebitax2 Dia')
  #eliminarEventoTitle('Pruebitax2 Dia')
  crearEvento("maybe va ;)", "esto es un evento de prueba", 41.3713, 2.1494, '2022-05-10T09:00:00','2022-05-10T10:00:00')
  #obtenerLocation(41.3713, 2.1494)
  #editarEventoTitle("maybe va ;)","Ya las visto")

if __name__ == '__main__':
   main()

