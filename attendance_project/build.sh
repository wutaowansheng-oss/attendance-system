#!/usr/bin/env bash
# Build script for Render

set -o errexit

pip install -r requirements.txt

# Create staticfiles directory if it doesn't exist
mkdir -p staticfiles

# Collect static files with verbose output
echo "==> Collecting static files..."
python manage.py collectstatic --noinput --clear --verbosity 2

echo "==> Static files collected successfully"

# Run migrations with verbose output
echo "==> Running migrations..."
python manage.py migrate --verbosity 2

echo "==> Migrations completed successfully"

# Create admin teacher if it doesn't exist
echo "==> Creating teacher accounts..."
python manage.py shell -c "
from attendance.models import Teacher
if not Teacher.objects.filter(teacher_id='admin').exists():
    Teacher.objects.create(name='Admin Teacher', teacher_id='admin', pin='admin123456')
    print('Admin teacher created: teacher_id=admin, pin=admin123456')
else:
    print('Admin teacher already exists')

if not Teacher.objects.filter(teacher_id='123456').exists():
    Teacher.objects.create(name='Teacher', teacher_id='123456', pin='232209')
    print('Teacher created: teacher_id=123456, pin=232209')
else:
    print('Teacher 123456 already exists')
"

echo "==> Build completed successfully!"
