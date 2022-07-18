from functions_calendar import crearEvento, editarEventoTitle, eliminarEventoID, buscarEventoTitle, eliminarEventoTitle, obtenerLocation

def main():

  # eliminarEvento('token') #funciona
  #buscarEventoTitle(stringtoken, 'Pruebitax2 Dia')
  #eliminarEventoTitle('Pruebitax2 Dia')
  crearEvento("token", "maybe va ;)", "esto es un evento de prueba", 41.3713, 2.1494, '2022-05-10T09:00:00','2022-05-10T10:00:00')
  #obtenerLocation(41.3713, 2.1494)
  #editarEventoTitle("maybe va ;)","Ya las visto")

if __name__ == '__main__':
   main()

