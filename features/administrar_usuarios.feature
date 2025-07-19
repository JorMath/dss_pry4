# language: es

Característica: Administración de usuarios por parte del Jefe de Seguridad

  Como Jefe de seguridad
  Quiero administrar los usuarios del sistema de incidentes
  Para controlar de mejor manera los reportes

  Escenario: Creación de un nuevo usuario
    Dado que el usuario a crear es "Jorman", con correo "jorman240802@gmail.com" y rol "analista"
    Cuando cree el usuario
    Entonces se enviará un correo a "jorman240802@gmail.com" con su contraseña temporal generada