from django.db import models

from sitech_models.soft_delete import SoftDeleteMixin
from sitech_models.tracking_fields import TrackingFieldsMixin


class Model(SoftDeleteMixin, TrackingFieldsMixin, models.Model):

    class Meta:
        abstract = True






