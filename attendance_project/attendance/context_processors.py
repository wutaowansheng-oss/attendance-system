def teacher_status(request):
    """Return a verified `is_teacher` boolean and `teacher_name` if session matches a Teacher.

    This function avoids side-effects and imports the `Teacher` model lazily to prevent
    circular import issues during template rendering.
    """
    tid = request.session.get('teacher_id')
    is_teacher = False
    teacher_name = None
    if tid:
        try:
            from .models import Teacher
            t = Teacher.objects.filter(teacher_id=tid).only('name').first()
            if t:
                is_teacher = True
                teacher_name = t.name
        except Exception:
            is_teacher = False
    return {'is_teacher': is_teacher, 'teacher_name': teacher_name}
