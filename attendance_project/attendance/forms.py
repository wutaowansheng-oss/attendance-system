from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'email', 'student_id']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
        }

class AttendanceSignForm(forms.Form):
    student_id = forms.CharField(
        max_length=64,
        label='Student ID',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your student ID'})
    )


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='CSV file', help_text='CSV with columns: name,student_id,email')


class AttendanceFilterForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))


class TeacherSignForm(forms.Form):
    teacher_id = forms.CharField(max_length=64, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Teacher ID')
    pin = forms.CharField(max_length=32, required=False, widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='PIN (optional)')
