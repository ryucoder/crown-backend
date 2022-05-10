from django.db import models


class TimeStampedModel(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class State(TimeStampedModel):
    name = models.CharField(max_length=255)
    gst_code = models.IntegerField()

    def __str__(self):
        return f"{self.name} - {self.gst_code}"

    class Meta:
        verbose_name = "State"
        verbose_name_plural = "States"


class District(TimeStampedModel):
    name = models.CharField(max_length=255)
    state = models.ForeignKey(
        "core.State", on_delete=models.PROTECT, related_name="districts"
    )

    def __str__(self):
        return f"{self.id} - {self.name} - {self.state}"

    class Meta:
        verbose_name = "District"
        verbose_name_plural = "Districts"


class City(TimeStampedModel):
    name = models.CharField(max_length=255)
    district = models.ForeignKey(
        "core.District", on_delete=models.PROTECT, related_name="cities"
    )

    def __str__(self):
        return f"{self.id} - {self.name} - {self.district}"

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"


class JobType(TimeStampedModel):
    option = models.CharField(max_length=255)

    def __str__(self):
        return self.option

    class Meta:
        verbose_name = "Job Type"
        verbose_name_plural = "Job Types"
