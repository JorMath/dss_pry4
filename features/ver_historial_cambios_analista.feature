Feature: Ver historial de cambios de incidentes como analista
  Como analista de seguridad
  Quiero poder ver un historial de cambios de cada incidente
  Para tener trazabilidad de su evolución

  Background:
    Given que soy un analista de seguridad autenticado en el sistema
    And existe un incidente reportado en estado "Pendiente"

  Scenario: Consultar historial de cambios de un incidente
    Given que existe un incidente con historial de cambios por múltiples analistas
    When consulte el historial de cambios del incidente
    Then debe ver todos los cambios realizados ordenados cronológicamente con usuario, fecha, campo modificado y valores anterior y nuevo
