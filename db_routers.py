class LogsRouter:
    """
    Envía las operaciones del modelo LogEntry a la base 'logs'.
    """

    route_app_labels = {'auditlog'}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'logs'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'logs'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Permite relaciones entre objetos de auditlog y cualquier otro objeto,
        incluso si están en diferentes bases.
        """
        if (
            obj1._meta.app_label in self.route_app_labels
            or obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == 'logs'
        return None
