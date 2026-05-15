from django.db import models

class IdealSignature(models.Model):
    sensor = models.CharField(max_length=50)
    values_json = models.TextField()  # JSON array stored as string
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"IdealSignature({self.sensor})"


class TankReading(models.Model):
    tank_id = models.CharField(max_length=50)
    sensor = models.CharField(max_length=50)
    values_json = models.TextField()
    timestamps_json = models.TextField()
    fault_type = models.CharField(max_length=50, default="none")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"TankReading({self.tank_id}, {self.sensor})"


class AnalysisResult(models.Model):
    tank_id = models.CharField(max_length=50)
    sensor = models.CharField(max_length=50)
    similarity_score = models.FloatField()
    status = models.CharField(max_length=20)
    first_deviation_index = models.IntegerField(null=True, blank=True)
    first_deviation_timestamp = models.CharField(max_length=50, null=True, blank=True)
    deviation_count = models.IntegerField(default=0)
    analyzed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-analyzed_at"]
