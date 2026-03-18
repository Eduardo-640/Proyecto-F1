from django.db import models


class Season(models.Model):
    name = models.CharField(max_length=100)
    year = models.PositiveSmallIntegerField()
    edition = models.PositiveSmallIntegerField()
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        ordering = ["year", "edition"]
        verbose_name = "Season"
        verbose_name_plural = "Seasons"

    def __str__(self):
        return f"{self.name} ({self.year}) - Edition {self.edition}"
