from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from .models import Student, Attendance, ClassSettings
from .forms import AttendanceSignForm, StudentForm
from .forms import CSVUploadForm, AttendanceFilterForm, TeacherSignForm
from django.http import HttpResponse
import csv
import io
from django.db import transaction
from django.utils.dateparse import parse_date
from datetime import datetime, time

def sign_in(request):
    # Ensure anonymous student users do not inherit any teacher session
    if not request.user.is_staff:
        request.session.pop('is_teacher', None)
        request.session.pop('teacher_id', None)
    if request.method == 'POST':
        form = AttendanceSignForm(request.POST)
        if form.is_valid():
            student_id = form.cleaned_data['student_id']
            try:
                student = Student.objects.get(student_id=student_id)
            except Student.DoesNotExist:
                messages.error(request, 'Student ID not found.')
                return redirect('attendance:sign_in')
            today = timezone.localdate()
            
            # Calculate status based on login time
            settings = ClassSettings.get_settings()
            now = timezone.now()
            login_time = now.time()
            
            # Compare login time with class start time
            status = 'present'
            if login_time > settings.class_start_time:
                late_threshold = timezone.datetime.combine(today, settings.class_start_time) + timezone.timedelta(minutes=settings.late_threshold_minutes)
                if now > late_threshold:
                    status = 'absent'
                else:
                    status = 'late'
            
            att, created = Attendance.objects.get_or_create(
                student=student, 
                date=today, 
                defaults={'status': status, 'login_time': login_time}
            )
            if created:
                if status == 'present':
                    messages.success(request, 'Attendance recorded. Thank you.')
                elif status == 'late':
                    messages.warning(request, 'Attendance recorded as LATE.')
                else:
                    messages.error(request, 'Attendance recorded as ABSENT (beyond late threshold).')
            else:
                messages.info(request, 'You have already signed in today.')
            return redirect('attendance:sign_in')
    else:
        form = AttendanceSignForm()
    return render(request, 'attendance/sign_in.html', {'form': form, 'is_teacher': False})

def teacher_or_staff_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if request.user.is_staff or request.session.get('is_teacher'):
            return view_func(request, *args, **kwargs)
        return redirect('attendance:teacher_sign_in')
    return _wrapped


@user_passes_test(lambda u: u.is_staff)
def student_list(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student added.')
            return redirect('attendance:student_list')
    else:
        form = StudentForm()
    students = Student.objects.all().order_by('name')
    is_teacher = request.user.is_staff or bool(request.session.get('is_teacher'))
    teacher_name = None
    if request.session.get('teacher_id'):
        try:
            from .models import Teacher
            t = Teacher.objects.filter(teacher_id=request.session.get('teacher_id')).only('name').first()
            if t:
                teacher_name = t.name
        except Exception:
            teacher_name = request.session.get('teacher_id')
    return render(request, 'attendance/student_list.html', {'students': students, 'form': form, 'is_teacher': is_teacher, 'teacher_name': teacher_name})


@teacher_or_staff_required
def manage_teachers(request):
    if request.method == 'POST':
        from .models import Teacher
        form = TeacherSignForm(request.POST)
        if form.is_valid():
            teacher_id = form.cleaned_data['teacher_id'].strip()
            pin = form.cleaned_data.get('pin', '').strip()
            try:
                t = Teacher.objects.get(teacher_id=teacher_id)
                messages.info(request, f'Teacher {t.name} already exists.')
            except Teacher.DoesNotExist:
                t = Teacher.objects.create(name=request.POST.get('name', teacher_id), teacher_id=teacher_id, pin=pin)
                messages.success(request, f'Teacher {t.name} created.')
            return redirect('attendance:manage_teachers')
    else:
        form = TeacherSignForm()
    from .models import Teacher
    teachers = Teacher.objects.all().order_by('name')
    is_teacher = request.user.is_staff or bool(request.session.get('is_teacher'))
    teacher_name = None
    if request.session.get('teacher_id'):
        try:
            t = Teacher.objects.filter(teacher_id=request.session.get('teacher_id')).only('name').first()
            if t:
                teacher_name = t.name
        except Exception:
            teacher_name = request.session.get('teacher_id')
    return render(request, 'attendance/manage_teachers.html', {'teachers': teachers, 'form': form, 'is_teacher': is_teacher, 'teacher_name': teacher_name})


@user_passes_test(lambda u: u.is_staff)
def delete_teacher(request, teacher_id):
    from .models import Teacher
    try:
        t = Teacher.objects.get(teacher_id=teacher_id)
        t.delete()
        messages.success(request, f'Teacher {t.name} deleted.')
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher not found.')
    return redirect('attendance:manage_teachers')


def teacher_sign_in(request):
    if request.method == 'POST':
        form = TeacherSignForm(request.POST)
        if form.is_valid():
            tid = form.cleaned_data['teacher_id'].strip()
            pin = form.cleaned_data.get('pin', '').strip()
            try:
                t = Student.objects.none()  # placeholder to avoid linter complaints
                from .models import Teacher
                teacher = Teacher.objects.get(teacher_id=tid)
            except Exception:
                messages.error(request, 'Teacher ID not found.')
                return redirect('attendance:teacher_sign_in')
            if teacher.pin and teacher.pin != pin:
                messages.error(request, 'Invalid PIN.')
                return redirect('attendance:teacher_sign_in')
            # successful sign-in
            request.session['is_teacher'] = True
            request.session['teacher_id'] = tid
            messages.success(request, f'Welcome, {teacher.name}.')
            return redirect('attendance:student_list')
    else:
        form = TeacherSignForm()
    return render(request, 'attendance/teacher_sign_in.html', {'form': form, 'is_teacher': False})


def teacher_sign_out(request):
    teacher_name = None
    if request.session.get('is_teacher'):
        # Get teacher name before clearing session
        from .models import Teacher
        try:
            teacher = Teacher.objects.get(teacher_id=request.session.get('teacher_id'))
            teacher_name = teacher.name
        except:
            pass
    
    request.session.pop('is_teacher', None)
    request.session.pop('teacher_id', None)
    request.session.flush()  # Clear entire session
    
    if teacher_name:
        messages.success(request, f'Goodbye, {teacher_name}. You have been signed out.')
    else:
        messages.info(request, 'Signed out successfully.')
    return redirect('attendance:sign_in')


@teacher_or_staff_required
def import_students(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data['csv_file']
            decoded = f.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded))
            created = 0
            updated = 0
            with transaction.atomic():
                for row in reader:
                    name = row.get('name') or row.get('Name')
                    student_id = row.get('student_id') or row.get('studentId') or row.get('student')
                    email = row.get('email') or row.get('Email') or ''
                    if not student_id:
                        continue
                    obj, was_created = Student.objects.update_or_create(
                        student_id=student_id.strip(),
                        defaults={'name': (name or '').strip(), 'email': (email or '').strip()}
                    )
                    if was_created:
                        created += 1
                    else:
                        updated += 1
            messages.success(request, f'Import complete: {created} created, {updated} updated.')
            return redirect('attendance:student_list')
    else:
        form = CSVUploadForm()
    is_teacher = request.user.is_staff or bool(request.session.get('is_teacher'))
    teacher_name = request.session.get('teacher_id')
    return render(request, 'attendance/import_students.html', {'form': form, 'is_teacher': is_teacher, 'teacher_name': teacher_name})


@teacher_or_staff_required
def export_attendance(request):
    form = AttendanceFilterForm(request.GET or None)
    start = None
    end = None
    if form.is_valid():
        start = form.cleaned_data.get('start_date')
        end = form.cleaned_data.get('end_date')
    qs = Attendance.objects.select_related('student').order_by('date')
    if start:
        qs = qs.filter(date__gte=start)
    if end:
        qs = qs.filter(date__lte=end)

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['student_id', 'name', 'date', 'status', 'timestamp'])
    for a in qs:
        writer.writerow([a.student.student_id, a.student.name, a.date.isoformat(), a.status, a.timestamp.isoformat()])
    return response


@teacher_or_staff_required
def attendance_report(request):
    form = AttendanceFilterForm(request.GET or None)
    start = form['start_date'].value() if form.is_bound else None
    end = form['end_date'].value() if form.is_bound else None
    start_date = parse_date(start) if start else None
    end_date = parse_date(end) if end else None

    students = Student.objects.all().order_by('name')
    report = []
    for s in students:
        qs = Attendance.objects.filter(student=s)
        if start_date:
            qs = qs.filter(date__gte=start_date)
        if end_date:
            qs = qs.filter(date__lte=end_date)
        present = qs.filter(status='present').count()
        late = qs.filter(status='late').count()
        total = qs.count()
        absent = qs.filter(status='absent').count()
        pct = (present / total * 100) if total else None
        report.append({'student': s, 'present': present, 'late': late, 'absent': absent, 'total': total, 'pct': pct})

    is_teacher = request.user.is_staff or bool(request.session.get('is_teacher'))
    teacher_name = request.session.get('teacher_id')
    return render(request, 'attendance/attendance_report.html', {
        'form': form, 
        'report': report, 
        'is_teacher': is_teacher, 
        'teacher_name': teacher_name,
        'start_date': start_date,
        'end_date': end_date
    })


@teacher_or_staff_required
def detailed_attendance_log(request):
    """Display detailed attendance log with login times and status"""
    from django.db.models import Q
    
    filter_date = request.GET.get('date')
    filter_student = request.GET.get('student')
    
    attendances = Attendance.objects.select_related('student').all().order_by('-date', 'student__name')
    
    if filter_date:
        attendances = attendances.filter(date=filter_date)
    if filter_student:
        attendances = attendances.filter(student__name__icontains=filter_student)
    
    settings = ClassSettings.get_settings()
    
    is_teacher = request.user.is_staff or bool(request.session.get('is_teacher'))
    teacher_name = request.session.get('teacher_id')
    
    return render(request, 'attendance/detailed_log.html', {
        'attendances': attendances,
        'settings': settings,
        'is_teacher': is_teacher,
        'teacher_name': teacher_name,
        'filter_date': filter_date,
        'filter_student': filter_student
    })


@teacher_or_staff_required
def class_settings(request):
    """Manage class settings like start time"""
    settings = ClassSettings.get_settings()
    
    if request.method == 'POST':
        try:
            start_time_str = request.POST.get('class_start_time')
            late_threshold = request.POST.get('late_threshold_minutes')
            
            if start_time_str:
                settings.class_start_time = start_time_str
            if late_threshold:
                settings.late_threshold_minutes = int(late_threshold)
            
            settings.save()
            messages.success(request, f'Settings updated. Class starts at {settings.class_start_time.strftime("%I:%M %p")}. Late threshold: {settings.late_threshold_minutes} minutes.')
        except Exception as e:
            messages.error(request, f'Error saving settings: {str(e)}')
        return redirect('attendance:class_settings')
    
    is_teacher = request.user.is_staff or bool(request.session.get('is_teacher'))
    teacher_name = request.session.get('teacher_id')
    
    return render(request, 'attendance/class_settings.html', {
        'settings': settings,
        'is_teacher': is_teacher,
        'teacher_name': teacher_name
    })

