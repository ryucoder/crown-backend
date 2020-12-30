import uuid 

from django.db import models


class TimeStampedModel(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PrimaryUUIDModel(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class PrimaryUUIDTimeStampedModel(PrimaryUUIDModel, TimeStampedModel):
    class Meta:
        abstract = True
