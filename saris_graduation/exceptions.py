
class CandidatesNotFoundException(Exception):
    message = "Candidate list not found"

    def __str__(self) -> str:
        return self.message


class GraduandsNotFoundException(Exception):
    message = "Graduation list not found"

    def __str__(self) -> str:
        return self.message