from django.contrib import admin
from import_export.admin import ExportActionModelAdmin

from .models import *


class GradeSchemeAdmin(ExportActionModelAdmin):
    list_display = ['min_grade', 'max_grade', 'letter_grade', 'grade_point', 'grade_quality', 'decision', 'grade_scheme_version']
    list_display_links = ['min_grade', 'max_grade','letter_grade']
    list_filter = ['letter_grade']


class AwardSchemeAdmin(ExportActionModelAdmin):
    list_display = ['program_type', 'min_cgpa', 'max_cgpa', 'repeated', 'award_class', 'description', 'assessment_version']
    list_display_links = ['program_type', 'min_cgpa', 'max_cgpa']
    list_filter = ['program_type']
 

class AssessmentRuleAdmin(ExportActionModelAdmin):
    list_display = [
        'program_type','min_cgpa', 'max_cgpa', 'is_first_year', 'is_repeating', 
        'has_failed_core', 'has_failed_sup', 'has_failed_cov', 'has_failed_rfc', 'decision', 'assessment_version'
    ]
    list_display_links = ['program_type', 'min_cgpa', 'max_cgpa']
    list_filter = ['program_type']


class CompensationRuleAdmin(ExportActionModelAdmin):
    list_display = [
        'program_level','withdrawal_semester', 'previous_semester', 'previous_result', 'award', 
    ]
    list_display_links = ['program_level', 'withdrawal_semester']
    list_filter = ['program_level']


class SemesterResultAdmin(ExportActionModelAdmin):
    list_display = [
        'enrollment', 'academic_semester', 'semester', 'semester_gpa', 'semester_credits', 
        'cumulative_gpa', 'cumulative_credits', 'decision','description'
    ]
    list_display_links = ['enrollment', 'academic_semester']
    search_fields = ['enrollment__student__student_number']
    list_filter = ['academic_semester', 'semester']

    
class StudentCourseAdmin(ExportActionModelAdmin):
    list_display = [
        'enrollment', 'academic_semester', 'course', 'course_type', 'course_attempt', 'semester',
        'continous_grade', 'endsemester_grade', 'final_grade', 'grade_point', 'letter_grade',
    ]
    list_display_links = ['enrollment', 'academic_semester']
    search_fields = ['enrollment__student__student_number', 'course__code']
    list_filter = ['academic_semester', 'semester']
    

class CourseAppealAdmin(ExportActionModelAdmin):
    list_display = [
        'enrollment', 'academic_semester', 'appeal_type',  'course', 'course_type', 'course_attempt', 'semester',
        'old_continous_grade', 'old_endsemester_grade',
        'continous_grade', 'endsemester_grade', 'status'
    ]
    list_display_links = ['enrollment', 'academic_semester', 'appeal_type']
    search_fields = ['enrollment__student__student_number']
    list_filter = ['academic_semester', 'appeal_type']

class SupplementaryAdmin(ExportActionModelAdmin):
    list_display = [
        'enrollment', 'academic_semester',  'course', 'course_type', 'course_attempt', 'semester',
        'continous_grade', 'endsemester_grade', 'status'
    ]
    list_display_links = ['enrollment', 'academic_semester']
    search_fields = ['enrollment__student__student_number']
    list_filter = ['academic_semester']


class LecturerCourseAdmin(ExportActionModelAdmin):
    list_display = ['lecturer',  'course']
    list_display_links = ['lecturer', 'course']
    

class GradeBenchMarkAdmin(ExportActionModelAdmin):
    list_display = ['continous_grade',  'endsemester_grade', 'version', 'is_active']
    list_display_links = ['continous_grade', 'endsemester_grade']


class PassMarkAdmin(ExportActionModelAdmin):
    list_display = ['program_type',  'pass_grade', 'pass_cgpa']
    list_display_links = ['program_type', 'pass_grade', 'pass_cgpa']
    
    
class PublishedResultAdmin(ExportActionModelAdmin):
    list_display = [
        'enrollment', 'academic_semester', 'semester', 'semester_gpa', 'semester_credits',
        'cumulative_gpa', 'cumulative_credits', 'decision', 'description'
    ]
    list_display_links = ['enrollment', 'academic_semester']
    search_fields = ['enrollment__student__student_number']
    list_filter = ['academic_semester', 'semester']


class PublishedGradeAdmin(ExportActionModelAdmin):
    list_display = [
        'enrollment', 'academic_semester', 'course', 'course_type', 'course_attempt', 'semester',
        'continous_grade', 'endsemester_grade', 'final_grade', 'grade_point', 'letter_grade',
    ]
    list_display_links = ['enrollment', 'academic_semester']
    search_fields = ['enrollment__student__student_number']
    list_filter = ['academic_semester', 'course', 'semester']


class GradeBookAdmin(ExportActionModelAdmin):
    list_display = [
        'faculty', 'academic_semester', 'status', 'pdf_file'
    ]
    list_display_links = ['faculty', 'academic_semester']
    list_filter = ['faculty', 'academic_semester']



admin.site.register(GradeScheme, GradeSchemeAdmin)
admin.site.register(AwardScheme, AwardSchemeAdmin)
admin.site.register(AssessmentRule, AssessmentRuleAdmin)
admin.site.register(CompensationRule, CompensationRuleAdmin)
admin.site.register(SemesterResult, SemesterResultAdmin)
admin.site.register(StudentCourse, StudentCourseAdmin)
admin.site.register(LecturerCourse, LecturerCourseAdmin)
admin.site.register(CourseAppeal, CourseAppealAdmin)
admin.site.register(Supplementary, SupplementaryAdmin)
admin.site.register(GradeBenchMark, GradeBenchMarkAdmin)
admin.site.register(PassMark, PassMarkAdmin)
admin.site.register(PublishedResult, PublishedResultAdmin)
admin.site.register(PublishedGrade, PublishedGradeAdmin)
admin.site.register(GradeBook, GradeBookAdmin)
admin.site.register(AssessmentVersion)
admin.site.register(GradeSchemeVersion)


