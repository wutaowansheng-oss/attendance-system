#!/usr/bin/env python
"""
Script to create default teacher accounts.
Run this from the project root: python create_teachers.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_project.settings')
django.setup()

from attendance.models import Teacher

# Create default teachers
teachers = [
    {'teacher_id': 'admin', 'name': 'Admin Teacher', 'pin': 'admin123456'},
    {'teacher_id': '123456', 'name': 'Teacher', 'pin': '232209'},
]

for teacher_data in teachers:
    teacher, created = Teacher.objects.get_or_create(
        teacher_id=teacher_data['teacher_id'],
        defaults={'name': teacher_data['name'], 'pin': teacher_data['pin']}
    )
    if created:
        print(f"✓ Created teacher: {teacher_data['teacher_id']} ({teacher_data['name']})")
    else:
        print(f"- Teacher already exists: {teacher_data['teacher_id']}")

print("\nDone! Teachers are ready to use.")
