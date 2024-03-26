
class ResultStatementNotFoundException(Exception):
    message = "Result statement not available"

    def __str__(self) -> str:
        return self.message
    

class SupplementaryNotFoundException(Exception):
    message = "Supplementary courses not available"

    def __str__(self) -> str:
        return self.message