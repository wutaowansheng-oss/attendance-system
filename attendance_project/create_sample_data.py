import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_project.settings')
django.setup()

from django.utils import timezone
from datetime import time
from attendance.models import Student, Attendance, ClassSettings

# Initialize class settings if not exists
settings = ClassSettings.get_settings()

# Get the students
try:
    aira = Student.objects.get(student_id="220209")
    ryan = Student.objects.get(student_id="232209")
    
    # Create attendance records for today
    today = timezone.localdate()
    
    # Aira Santino - Present (logged in at 7:50 AM - before class start at 8:00 AM)
    present_time = time(7, 50, 0)
    Attendance.objects.update_or_create(
        student=aira,
        date=today,
        defaults={'status': 'present', 'login_time': present_time}
    )
    print(f"✓ Aira Santino: Present at {present_time.strftime('%I:%M %p')}")
    
    # Ryan James Clemente - Late (logged in at 8:15 AM - within 30 min threshold)
    late_time = time(8, 15, 0)
    Attendance.objects.update_or_create(
        student=ryan,
        date=today,
        defaults={'status': 'late', 'login_time': late_time}
    )
    print(f"✓ Ryan James Clemente: Late at {late_time.strftime('%I:%M %p')}")
    
    print(f"\nClass Settings: {settings}")
    print(f"Present: Login at or before {settings.class_start_time.strftime('%I:%M %p')}")
    print(f"Late: Login between {settings.class_start_time.strftime('%I:%M %p')} and {settings.late_threshold_minutes} minutes after")
    
except Student.DoesNotExist as e:
    print(f"Student not found: {e}")
