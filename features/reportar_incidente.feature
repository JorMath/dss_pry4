# language: es

Característica: Reportar incidente de seguridad (HU01)
  
  Narrativa:
  Como usuario reportante, quiero registrar un incidente de seguridad proporcionando su tipo, descripción y fecha, para que el equipo de seguridad lo gestione.
  
  Criterios de aceptación:
  - Se muestra un formulario con campos: tipo de incidente, descripción, fecha.
  - Todos los campos son obligatorios.
  - El incidente queda registrado con estado "pendiente".
  - Se confirma el envío con un mensaje en pantalla.

  Escenario: Reportar un incidente correctamente
    Dado que el Usuario reportante tiene un incidente de tipo "bug" con descripción "este bug permite escribir en la base de datos sin autorización" con fecha "07-06-2025"
    Cuando reporte el incidente
    Entonces el incidente se registra con el estado "pendiente" y gravedad "alta"
    Y se notifica al Usuario reportante que se ha realizado el reporte correctamente
