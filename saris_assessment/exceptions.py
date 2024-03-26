class AssessmentRuleNotFoundException(Exception):
    message = "Result not matching assessment rules"

    def __str__(self) -> str:
        return self.message


class GradeBenchMarkNotFoundException(Exception):
    message = "Grade benchmark not configured"

    def __str__(self) -> str:
        return self.message
    

class PassMarkNotFoundException(Exception):
    message = "Grade Passmark not configured"

    def __str__(self) -> str:
        return self.message


class CASBenchMarkError(Exception):
    __student = None
    def __init__(self, student, *args: object) -> None:
        self.__student = student
        super().__init__(*args)
    
    def __str__(self) -> str:
        student = self.__student
        return f"Student ({student}) CAS GRADE exceeds benchmark"


class EOSBenchMarkError(Exception):
    __student = None

    def __init__(self, student, *args: object) -> None:
        self.__student = student
        super().__init__(*args)

    def __str__(self) -> str:
        student = self.__student
        return f"Student ({student}) EOS GRADE exceeds benchmark"


class AssessmentVersionNotFoundException(Exception):
    message = "Assessment version not found"

    def __str__(self) -> str:
        return self.message


class GradeSchemeVersionNotFoundException(Exception):
    message = "Grade scheme version not found"

    def __str__(self) -> str:
        return self.message
    

class ExamResultsNotFoundException(Exception):
    message = "Examination results not available"

    def __str__(self) -> str:
        return self.message
    

class CourseAppealsNotFoundException(Exception):
    message = "Course appeals not available"

    def __str__(self) -> str:
        return self.message
    

class SupplementaryNotFoundException(Exception):
    message = "Supplementary courses not available"

    def __str__(self) -> str:
        return self.message