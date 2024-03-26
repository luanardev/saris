from django import forms
from saris_assessment.models import CourseAttempt, StudentCourse
from saris_calendar.filters import get_academic_semester_by_campus
from saris_curriculum.services import CurriculumManager
from saris_registration.models import Registration

class RegisterForm(forms.ModelForm):
    student_number = forms.IntegerField(required=True, label="Student number")
    academic_semester = forms.ModelChoiceField(required=True, queryset=None)
    
    class Meta:
        model = Registration
        fields = ['student_number', 'academic_semester']
        exclude = ['enrollment',  'academic_semester','semester', 'type', 'status',]

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields["academic_semester"].queryset = get_academic_semester_by_campus(request)


class StudentCourseForm(forms.ModelForm):
    course_attempt = forms.ChoiceField(required=True, choices=CourseAttempt.choices)
    course = forms.ModelChoiceField(required=True, queryset=None)

    class Meta:
        model = StudentCourse
        fields = ['course', 'course_attempt']

    def __init__(self,  *args, **kwargs):
        self.registration = kwargs.pop('registration', None)
        self.enrollment = self.registration.enrollment
        self.academic_semester = self.registration.academic_semester
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = self.get_curriculum_courses()

    def get_curriculum_courses(self):
        manager = CurriculumManager(
            program=self.enrollment.program,
            semester=self.enrollment.semester,
            academic_semester=self.academic_semester
        )
        return manager.get_program_courses()
