from django.db import models


class Model(models.Model):
    tracker_fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._old_fields = {}
        for field in self.tracker_fields:
            self._old_fields[field] = getattr(self, field)

    def get_old_field(self, field, default=None):
        if field in self._old_fields:
            return self._old_fields[field]
        return default

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        result = super().save(force_insert, force_update, using, update_fields)
        self._old_fields = {}
        return result

    class Meta:
        abstract = True