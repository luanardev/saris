from django import forms
from django.core.validators import FileExtensionValidator
from account.models import Staff
from saris_curriculum.models import Course, StatusType
from saris_assessment.models import CourseAppeal, LecturerCourse

class ImportForm(forms.Form):
    file = forms.FileField(
        widget=forms.FileInput(attrs={'accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}),
        required=True,
        label="Excel File",
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        help_text="Upload Excel sheet"
    )

class CourseAllocationForm(forms.ModelForm):
    course = forms.ModelChoiceField(
        queryset=None, 
        required=True, 
        label="Courses", 
        widget=forms.SelectMultiple()
    )
    class Meta:
        model = LecturerCourse
        fields = ['lecturer', 'course']

    def __init__(self,  *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        department = request.user.staff.department
        self.fields['course'].queryset = self.get_courses_not_assigned(department)
        self.fields['lecturer'].queryset = self.get_lecturers(department)

    def get_courses_not_assigned(self, department):
        course_id_list = LecturerCourse.filter(course__department=department).values_list('course_id')
        courses_not_assigned = Course.filter(department=department, status=StatusType.ACTIVE).exclude(id__in=course_id_list)
        return courses_not_assigned

    def get_lecturers(self, department):
        return Staff.objects.filter(department=department)
    

class AppealGradeForm(forms.ModelForm):
    continous_grade = forms.IntegerField(required=True, label="CAS Grade")
    endsemester_grade = forms.IntegerField(required=True, label="EOS Grade")
    class Meta:
        model = CourseAppeal
        fields = ['continous_grade', 'endsemester_grade']