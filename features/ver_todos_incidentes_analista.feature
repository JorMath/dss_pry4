Feature: Ver todos los incidentes de seguridad como analista
  Como analista de seguridad
  Quiero ver todos los incidentes reportados en el sistema
  Para poder analizarlos y gestionarlos adecuadamente

  Background:
    Given que soy un analista de seguridad autenticado en el sistema
    And que hay incidentes reportados

  Scenario: Visualización de todos los incidentes
    Given que hay incidentes reportados
    When visualice los incidentes reportados
    Then debe ver una lista con todos los incidentes registrados por su fecha, tipo, descripción, gravedad, y el Usuario Reportante que lo hizo
