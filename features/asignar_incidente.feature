# language: es
Característica: HU10 - Asignación de incidente
  Como jefe de seguridad
  Quiero asignar incidentes a analistas de seguridad
  Para distribuir la carga de trabajo eficientemente

  Antecedentes:
    Dado que existen usuarios: jefe "María López", analistas "Ana García" y "Luis Martín"
    Y existe un incidente pendiente ID "123"
    Y existe un incidente asignado ID "125" a "Luis Martín"
    Y estoy autenticado como jefe de seguridad

  Escenario: Asignar incidente a analista
    Cuando asigne el incidente "123" al analista "Ana García"
    Entonces el incidente queda asignado a "Ana García"
    Y se confirma con mensaje de éxito

  Escenario: Reasignar incidente
    Cuando reasigne el incidente "125" de "Luis Martín" a "Ana García"
    Entonces el incidente cambia de asignación a "Ana García"
    Y se confirma la reasignación

  Escenario: Ver estado de asignación
    Dado que estoy en la lista de incidentes
    Entonces veo la columna "Asignado a"
    Y los incidentes muestran su estado de asignación
