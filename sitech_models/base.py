from django.db import models


class TrackingFieldsMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._old_fields = {}
        self._set_old_fields()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        result = super().save(force_insert, force_update, using, update_fields)
        self._set_old_fields()
        return result

    def _set_old_fields(self):
        for field in self._meta.fields:
            attname, column = field.get_attname_column()
            self._old_fields[column] = getattr(self, column)

    def get_old_field(self, field, default=None):
        if field in self._old_fields:
            return self._old_fields[field]
        return default

    def set_old_field(self, field, value):
        self._old_fields[field] = value


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self, force_delete=False):
        if force_delete:
            return super().delete()
        return super().update(is_deleted=1)


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(model=self.model, using=self._db, hints=self._hints).filter(is_deleted=False)


class SoftDeleteMixin(models.Model):
    is_deleted = models.BooleanField(default=False)

    objects = SoftDeleteManager()

    def delete(self, using=None, keep_parents=False, force_delete=False):
        if force_delete:
            return super().delete(using=using, keep_parents=keep_parents)
        self.is_deleted = True
        self.save()

    class Meta:
        abstract = True


class Model(SoftDeleteMixin, TrackingFieldsMixin, models.Model):

    class Meta:
        abstract = True






