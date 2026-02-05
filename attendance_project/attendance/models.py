from django.db import models
from django.utils import timezone
from datetime import time

class Student(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    student_id = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.student_id})"

class Attendance(models.Model):
    STATUS_CHOICES = [
        ("present", "Present"),
        ("late", "Late"),
        ("absent", "Absent"),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendances")
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="present")
    timestamp = models.DateTimeField(auto_now_add=True)
    login_time = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ("student", "date")

    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"


class Teacher(models.Model):
    name = models.CharField(max_length=200)
    teacher_id = models.CharField(max_length=64, unique=True)
    pin = models.CharField(max_length=32, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.teacher_id})"


class ClassSettings(models.Model):
    class_start_time = models.TimeField(default=time(8, 0), help_text="Class start time (8:00 AM by default)")
    late_threshold_minutes = models.IntegerField(default=30, help_text="Minutes after start time to mark as late (default: 30 min)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Class Settings"

    def __str__(self):
        return f"Class Start: {self.class_start_time.strftime('%I:%M %p')}"

    @staticmethod
    def get_settings():
        obj, created = ClassSettings.objects.get_or_create(id=1)
        return obj
