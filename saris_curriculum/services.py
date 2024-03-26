
from .exceptions import MasterCurriculumMissingException
from .models import ConfiguredCourse, ConfiguredCurriculum, MasterCurriculum


class CurriculumConfigurator(object):
    
    def __init__(self, program, semester, academic_semester):
        self.program = program
        self.academic_semester = academic_semester
        self.semester = semester  
        
    def has_master(self):
        exists = MasterCurriculum.objects.filter(program=self.program, semester=self.semester).exists()
        return exists
        
    def is_configured(self):
        exists = ConfiguredCurriculum.objects.filter(program=self.program, academic_semester=self.academic_semester, semester=self.semester).exists()
        return exists 

    def get_master(self):
        curriculum = MasterCurriculum.objects.filter(program=self.program, semester=self.semester)
        return curriculum
    
    def configure(self):
        if not self.has_master():
            raise MasterCurriculumMissingException
        
        if self.is_configured():
            raise Exception("Master Curriculum already Configured")
            
        curriculum = ConfiguredCurriculum()
        curriculum.academic_semester=self.academic_semester
        curriculum.program=self.program
        curriculum.semester=self.semester
        curriculum.version=self.program.version
        curriculum.save()
        
        master_courses = self.get_master()
        
        for master in master_courses:
            configured = ConfiguredCourse()
            configured.curriculum=curriculum
            configured.course=master.course
            configured.course_type=master.course_type
            configured.semester=master.semester
            configured.save()
            
        return curriculum
           

class CurriculumManager(object):
    
    def __init__(self, program, semester, academic_semester=None) -> None:
        self.program = program
        self.semester = semester
        self.academic_semester = academic_semester
     
    def get_master_curriculum(self) -> MasterCurriculum:
        return MasterCurriculum.objects.filter(
            program=self.program,
            semester=self.semester
        )
        
    def get_program_courses(self) -> MasterCurriculum:
        return MasterCurriculum.objects.filter(
            program=self.program
        )

    def get_configured_curriculum(self) -> ConfiguredCurriculum:
        return ConfiguredCurriculum.objects.filter(
            academic_semester=self.academic_semester,
            program=self.program,
            semester=self.semester
        ).first()

    def has_master_curriculum(self) -> bool:
        return MasterCurriculum.objects.filter(
            program=self.program,
            semester=self.semester
        ).exists()
        
    def has_configured_curriculum(self) -> bool:
        return ConfiguredCurriculum.objects.filter(
            academic_semester=self.academic_semester,
            program=self.program,
            semester=self.semester
        ).exists()

    def check_master_curriculum(self) -> bool:
        if not self.has_master_curriculum():
            raise MasterCurriculumMissingException
        else:
            return True
        
    def get_courses(self):
        curriculum = self.get_configured_curriculum()
        if curriculum:
            return curriculum.courses()
        else:
            return self.get_master_curriculum()