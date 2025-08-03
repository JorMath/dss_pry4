# language: es
Característica: HU09 - Gestionar usuarios del sistema
  Como jefe de seguridad
  Quiero listar todos los usuarios del sistema ordenados por rol y username
  Para supervisar el equipo y mantener control de los accesos

  Antecedentes:
    Dado que existen usuarios con diferentes roles en el sistema
    Y estoy autenticado como jefe de seguridad

  Escenario: Listar todos los usuarios del sistema
    Cuando acceda a "Listar usuarios"
    Entonces veo todos los usuarios ordenados por rol
    Y veo la información completa de cada usuario
    Y veo las estadísticas de usuarios por rol

  Escenario: Verificar información mostrada de usuarios
    Dado que estoy en la lista de usuarios
    Entonces cada usuario muestra: username, nombre, email descifrado y rol
    Y los usuarios están agrupados por rol

  Escenario: Validar acceso solo para jefes
    Dado que estoy autenticado como un usuario con rol "analista"
    Cuando intente acceder a "Listar usuarios"
    Entonces el sistema me redirige por falta de permisos
