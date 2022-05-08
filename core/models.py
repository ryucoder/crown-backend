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


class State(PrimaryUUIDTimeStampedModel):
    name = models.CharField(max_length=255)
    gst_code = models.IntegerField()

    def __str__(self):
        return f"{self.name} - {self.gst_code}"

    class Meta:
        verbose_name = "State"
        verbose_name_plural = "States"


class JobType(PrimaryUUIDTimeStampedModel):
    option = models.CharField(max_length=255)

    def __str__(self):
        return self.option

    class Meta:
        verbose_name = "Job Type"
        verbose_name_plural = "Job Types"
