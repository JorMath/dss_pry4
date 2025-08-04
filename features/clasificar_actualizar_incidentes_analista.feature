Feature: Clasificar y actualizar incidentes como analista
  Como analista de seguridad
  Quiero poder clasificar y actualizar los incidentes de seguridad
  Para mantener un seguimiento adecuado del estado y gravedad de cada caso

  Background:
    Given que soy un analista de seguridad autenticado en el sistema
    And existe un incidente reportado en estado "Pendiente"

  Scenario: Clasificar y cambiar estado de un incidente
    Given que hay un incidente reportado en gravedad "alta" con el analista "Juan"
    When el analista "Juan" cambie el tipo de gravedad a "baja"
    Then el incidente tendrá la gravedad a "baja" Y se actualizará la última modificación por "Juan"
