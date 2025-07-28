# language: es

Característica: Ver mis incidentes reportados (HU02)
  
  Narrativa:
  Como usuario reportante, quiero ver los incidentes que he reportado, para darles seguimiento y conocer su estado.
  
  Criterios de aceptación:
  - El sistema muestra una lista de mis incidentes con: tipo, estado, fecha.
  - Solo se muestran incidentes creados por el usuario actual.

  Escenario: Ver lista de incidentes reportados por el usuario
    Dado que el Usuario reportante tiene al menos un incidente reportado
    Cuando quiera ver los incidentes que ha reportado
    Entonces se mostrará una lista de incidentes que ha reportado

  Escenario: Usuario Reportante no tiene incidentes reportados
    Dado que el Usuario Reportante no tiene incidentes reportados
    Cuando quiera ver los incidentes que ha reportado
    Entonces se notifica al Usuario reportante que no ha reportado ningún incidente
    Y se le permite regresar a las opciones de registro de incidentes
