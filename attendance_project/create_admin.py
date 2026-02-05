#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "attendance_project.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("manage.py") from exc
    
    # Create superuser with predefined credentials
    sys.argv = ["manage.py", "createsuperuser", "--noinput", "--username", "admin", "--email", "admin@school.com"]
    execute_from_command_line(sys.argv)
    
    # Set password
    from django.contrib.auth.models import User
    user = User.objects.get(username="admin")
    user.set_password("admin123456")
    user.save()
    print("✅ Superuser 'admin' created with password 'admin123456'")
