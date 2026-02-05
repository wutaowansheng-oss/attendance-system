import os
import django

# Set up Django with PostgreSQL
os.environ['DATABASE_URL'] = 'postgresql://attendance_user:PYKVSPqg712XvwitnQiePHWXOs3050k3@dpg-d603lr3uibrs73d6mddg-a.oregon-postgres.render.com/attendance_isid'
os.environ['DB_ENGINE'] = 'postgresql'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_project.settings')

django.setup()

from django.contrib.auth.models import User

# Create superuser
username = input("Enter username for superuser: ")
email = input("Enter email for superuser: ")
password = input("Enter password for superuser: ")

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"✅ Superuser '{username}' created successfully!")
else:
    print(f"❌ User '{username}' already exists!")
