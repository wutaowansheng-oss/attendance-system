from django.contrib import admin
from .models import Student, Attendance

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "student_id", "email", "created_at")
    search_fields = ("name", "student_id", "email")

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "status", "timestamp")
    list_filter = ("date", "status")
    search_fields = ("student__name", "student__student_id")

# Teacher management moved to custom view to avoid admin template issues
