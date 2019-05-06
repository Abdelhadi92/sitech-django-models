from collections import Counter
from operator import attrgetter

from django.conf import settings
from django.db import models
from django.db import transaction, router
from django.db.models import signals, sql
from django.db.models.deletion import Collector


class SoftDeleteCollector(Collector):

    def delete(self):
        # sort instance collections
        for model, instances in self.data.items():
            self.data[model] = sorted(instances, key=attrgetter("pk"))

        # if possible, bring the models in an order suitable for databases that
        # don't support transactions or cannot defer constraint checks until the
        # end of a transaction.
        self.sort()
        # number of objects deleted for each model label
        deleted_counter = Counter()

        with transaction.atomic(using=self.using, savepoint=False):
            # send pre_delete signals
            for model, obj in self.instances_with_model():
                if not model._meta.auto_created:
                    signals.pre_delete.send(
                        sender=model, instance=obj, using=self.using
                    )

            # fast deletes
            for qs in self.fast_deletes:
                pk_list = [obj.pk for obj in qs]
                if pk_list:
                    query = sql.UpdateQuery(qs.model)
                    query.update_batch([obj.pk for obj in qs], {'is_deleted': True}, self.using)
                # deleted_counter[qs.model._meta.label] += count

            # reverse instance collections
            for instances in self.data.values():
                instances.reverse()

            # delete instances
            for model, instances in self.data.items():
                pk_list = [obj.pk for obj in instances]
                if pk_list:
                    query = sql.UpdateQuery(model)
                    query.update_batch(pk_list, {'is_deleted': True}, self.using)
                # deleted_counter[model._meta.label] += count

                if not model._meta.auto_created:
                    for obj in instances:
                        signals.post_delete.send(
                            sender=model, instance=obj, using=self.using
                        )

        # update collected instances
        for model, instances_for_fieldvalues in self.field_updates.items():
            for (field, value), instances in instances_for_fieldvalues.items():
                for obj in instances:
                    setattr(obj, field.attname, value)
        for model, instances in self.data.items():
            for instance in instances:
                setattr(instance, model._meta.pk.attname, None)
        return sum(deleted_counter.values()), dict(deleted_counter)


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self, force_delete=False):
        if force_delete or not getattr(settings, 'SOFT_DELETE', False):
            return super().delete()

        assert self.query.can_filter(), \
            "Cannot use 'limit' or 'offset' with delete."

        if self._fields is not None:
            raise TypeError("Cannot call delete() after .values() or .values_list()")

        del_query = self._chain()

        # The delete is actually 2 queries - one to find related objects,
        # and one to delete. Make sure that the discovery of related
        # objects is performed on the same database as the deletion.
        del_query._for_write = True

        # Disable non-supported fields.
        del_query.query.select_for_update = False
        del_query.query.select_related = False
        del_query.query.clear_ordering(force_empty=True)

        collector = SoftDeleteCollector(using=del_query.db)
        collector.collect(del_query)
        deleted, _rows_count = collector.delete()

        # Clear the result cache, in case this QuerySet gets reused.
        self._result_cache = None
        return deleted, _rows_count


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(model=self.model, using=self._db, hints=self._hints).filter(is_deleted=False)


class SoftDeleteMixin(models.Model):
    is_deleted = models.BooleanField(default=False)

    objects = SoftDeleteManager()

    def delete(self, using=None, keep_parents=False, force_delete=False):
        if force_delete or not getattr(settings, 'SOFT_DELETE', False):
            return super().delete(using=using, keep_parents=keep_parents)

        using = using or router.db_for_write(self.__class__, instance=self)
        assert self.pk is not None, (
                "%s object can't be deleted because its %s attribute is set to None." %
                (self._meta.object_name, self._meta.pk.attname)
        )
        collector = SoftDeleteCollector(using=using)
        collector.collect([self], keep_parents=keep_parents)
        return collector.delete()

    class Meta:
        abstract = True