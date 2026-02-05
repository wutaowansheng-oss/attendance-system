from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('sign-in/', views.sign_in, name='sign_in'),
    path('students/', views.student_list, name='student_list'),
    path('import-students/', views.import_students, name='import_students'),
    path('export-attendance/', views.export_attendance, name='export_attendance'),
    path('report/', views.attendance_report, name='attendance_report'),
    path('detailed-log/', views.detailed_attendance_log, name='detailed_log'),
    path('class-settings/', views.class_settings, name='class_settings'),
    path('teacher-sign-in/', views.teacher_sign_in, name='teacher_sign_in'),
    path('teacher-sign-out/', views.teacher_sign_out, name='teacher_sign_out'),
    path('manage-teachers/', views.manage_teachers, name='manage_teachers'),
    path('delete-teacher/<str:teacher_id>/', views.delete_teacher, name='delete_teacher'),
    path('', views.sign_in, name='home'),
]
