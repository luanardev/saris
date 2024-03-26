class MasterCurriculumMissingException(Exception):
    message = "Master curriculum not found"
    
    def __str__(self) -> str:
        return self.message