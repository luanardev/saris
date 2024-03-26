import django_tables2 as tables
from saris.tables import SelectAllCheckBoxColumn
from saris_graduation.models import Booklet, Candidate, Session


class SessionTable(tables.Table):

    name = tables.Column(
        verbose_name="SESSION",
        accessor="name",
        linkify=("graduation:session.update", [tables.A("pk")] )
    )
     
    academic_year = tables.Column(
        verbose_name="ACADEMIC YEAR",
        accessor="academic_year",
    )

    graduation_date = tables.Column(
        verbose_name="GRADUATION DATE",
        accessor="graduation_date",
    )

    action = tables.LinkColumn(
        verbose_name="ACTION",
        viewname="graduation:candidate.browse", 
        text="Candidates", 
        args=[tables.A("pk")]
    )
    
    class Meta:
        model = Session
        fields = ['name', 'academic_year', 'graduation_date', 'action']
        

class CandidateTable(tables.Table):
  
    student_number = tables.Column(
        verbose_name="STUDENT NUMBER",
        accessor="enrollment__student__student_number",
        linkify=("graduation:candidate.details", [tables.A("pk")] )
    )
     
    first_name = tables.Column(
        verbose_name="FIRST NAME",
        accessor="enrollment__student__first_name",
        linkify=("graduation:candidate.details", [tables.A("pk")] )
    )

    last_name = tables.Column(
        verbose_name="LAST NAME",
        accessor="enrollment__student__last_name",
        linkify=("graduation:candidate.details", [tables.A("pk")] )
    )

    middle_name = tables.Column(
        verbose_name="MIDDLE NAME",
        accessor="enrollment__student__middle_name",
    )
    
    award_name = tables.Column(
        verbose_name="AWARD NAME",
        accessor="enrollment__award_name",
    )

    award_class = tables.Column(
        verbose_name="AWARD CLASS",
        accessor="enrollment__award_class",
    )

    faculty = tables.Column(
        verbose_name="FACULTY",
        accessor="enrollment__program__department__faculty",
    )
    
    campus = tables.Column(
        verbose_name="CAMPUS",
        accessor="enrollment__campus",
    )

    
    class Meta:
        model = Candidate
        fields = ['student_number', 'first_name', 'last_name', 'middle_name', 'award_name', 'award_class', 'faculty', 'campus',]
        

class BookletTable(tables.Table):
    selection = SelectAllCheckBoxColumn(accessor="pk", orderable=False)
   
    session = tables.Column(
        verbose_name="SESSION",
        accessor="session",
        linkify=("graduation:booklet.download", [tables.A("pk")] )
    )
     
    status = tables.Column(
        verbose_name="STATUS",
        accessor="status",
    )
    
    created_at = tables.Column(
        verbose_name="GENERATED ON",
        accessor="created_at",
    )

    class Meta:
        model = Booklet
        fields = ['selection', 'session', 'status', 'created_at']
        

