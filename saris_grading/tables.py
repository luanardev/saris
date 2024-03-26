import django_tables2 as tables
from saris_assessment.models import StudentCourse


class ClassListTable(tables.Table):
    student_number = tables.Column(
        verbose_name="ID",
        accessor="enrollment__student__student_number")

    student = tables.Column(
        verbose_name="STUDENT",
        accessor="enrollment__student")
    
    program = tables.Column(
        verbose_name="PROGRAM",
        accessor="enrollment__program")
    
    semester = tables.Column(
        verbose_name="SEMESTER",
        accessor="semester")
    
    class Meta:
        model = StudentCourse
        fields = ['student_number', 'student', 'program', 'semester',]
        

class GradeTemplateTable(tables.Table):
    student_number = tables.Column(
        verbose_name="STUDENT_NUMBER",
        accessor="enrollment__student__student_number")
    
    student = tables.Column(
        verbose_name="STUDENT_NAME",
        accessor="enrollment__student")
    
    program_code = tables.Column(
        verbose_name="PROGRAM_CODE",
        accessor="enrollment__program__code")
    
    mid_semester = tables.Column(
        verbose_name="CAS_GRADE",
        accessor="continous_grade")
    
    end_semester = tables.Column(
        verbose_name="EOS_GRADE",
        accessor="endsemester_grade")
    
    class Meta:
        model = StudentCourse
        fields = ['student_number', 'student', 'program_code',  'mid_semester', 'end_semester']


class ResultsheetTable(tables.Table):
    student_number = tables.Column(
        verbose_name="ID",
        accessor="enrollment__student__student_number")

    student = tables.Column(
        verbose_name="STUDENT",
        accessor="enrollment__student")
    
    program_code = tables.Column(
        verbose_name="PROGRAM CODE",
        accessor="enrollment__program__code")
    
    continous_grade = tables.Column(
        verbose_name="CAS GRADE",
        accessor="continous_grade")
    
    endsemester_grade = tables.Column(
        verbose_name="EOS GRADE",
        accessor="endsemester_grade")
    
    final_grade = tables.Column(
        verbose_name="FINAL GRADE",
        accessor="final_grade")
    
    final_grade = tables.Column(
        verbose_name="FINAL GRADE",
        accessor="final_grade")
    
    grade_point = tables.Column(
        verbose_name="GRADE POINT",
        accessor="grade_point")
    
    letter_grade = tables.Column(
        verbose_name="LETTER GRADE",
        accessor="letter_grade")
    
    class Meta:
        model = StudentCourse
        fields = [
            'student_number','student', 'program_code','continous_grade',
            'endsemester_grade', 'final_grade','grade_point','letter_grade'
        ]
