from django.db import models

# Create your models here.

class Candidate(models.Model):
    name = models.CharField(max_length=200)
    graduation_year = models.IntegerField(null=True, blank=True)
    class_10_year = models.IntegerField(null=True, blank=True)
    class_12_year = models.IntegerField(null=True, blank=True)  # Allow null values
    class_10_marks = models.FloatField(null=True, blank=True)
    class_12_marks = models.FloatField(null=True, blank=True)
    experience_years = models.IntegerField(default=0)
    last_job_title = models.CharField(max_length=200, blank=True)
    companies = models.TextField(blank=True)
    cities = models.TextField(blank=True)
    college = models.CharField(max_length=200, blank=True)
    extracurricular_activities = models.TextField(blank=True)
    certificates = models.TextField(blank=True)

    def __str__(self):
        return self.name