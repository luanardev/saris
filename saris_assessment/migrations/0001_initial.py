# Generated by Django 5.0.2 on 2024-03-12 11:32

import dirtyfields.dirtyfields
import django.db.models.deletion
import saris.models
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
        ('saris_admission', '0001_initial'),
        ('saris_calendar', '0001_initial'),
        ('saris_curriculum', '0001_initial'),
        ('saris_institution', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssessmentVersion',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.BigAutoField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('version', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Assessment Version',
                'verbose_name_plural': 'assessment version',
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='CompensationRule',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.BigAutoField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('program_level', models.CharField(choices=[('SHORTCOURSE', 'Shortcourse'), ('CERTIFICATE', 'Certificate'), ('DIPLOMA', 'Diploma'), ('BACHELORS', 'Bachelors'), ('HONOURS', 'Honours'), ('PG_CERTIFICATE', 'Pg Certificate'), ('PG_DIPLOMA', 'Pg Diploma'), ('MASTERS', 'Masters'), ('DOCTORATE', 'Doctorate')], max_length=255)),
                ('withdrawal_semester', models.IntegerField()),
                ('previous_semester', models.IntegerField()),
                ('previous_result', models.CharField(choices=[('PAP', 'Pap'), ('PCO', 'Pco'), ('RFC', 'Rfc'), ('FAW', 'Faw'), ('SUP', 'Sup'), ('MGD', 'Mgd'), ('SAW', 'Saw'), ('SUP_RFC', 'Sup Rfc'), ('RFC_PCO', 'Rfc Pco'), ('RFC_RFC', 'Rfc Rfc')], default='PAP', max_length=255)),
                ('award', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Compensation Rule',
                'verbose_name_plural': 'compensation rule',
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='GradeBenchMark',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('continous_grade', models.FloatField()),
                ('endsemester_grade', models.FloatField()),
                ('version', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Grade Bench Mark',
                'verbose_name_plural': 'grade benchmark',
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='GradeSchemeVersion',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.BigAutoField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('version', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Grade Scheme Version',
                'verbose_name_plural': 'grade scheme version',
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='PassMark',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.BigAutoField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('program_type', models.CharField(choices=[('UNDERGRADUATE', 'Undergraduate'), ('POSTGRADUATE', 'Postgraduate')], max_length=255)),
                ('pass_grade', models.FloatField()),
                ('pass_cgpa', models.FloatField()),
            ],
            options={
                'verbose_name': 'Grade Pass Mark',
                'verbose_name_plural': 'grade passmark',
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='AssessmentRule',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.BigAutoField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('program_type', models.CharField(choices=[('UNDERGRADUATE', 'Undergraduate'), ('POSTGRADUATE', 'Postgraduate')], max_length=255)),
                ('min_cgpa', models.FloatField()),
                ('max_cgpa', models.FloatField()),
                ('continuing', models.BooleanField(default=False)),
                ('repeating', models.BooleanField(default=False)),
                ('failed_core', models.BooleanField(default=False)),
                ('failed_sup', models.BooleanField(default=False)),
                ('failed_cov', models.BooleanField(default=False)),
                ('failed_rfc', models.BooleanField(default=False)),
                ('decision', models.CharField(choices=[('PAP', 'Pap'), ('PCO', 'Pco'), ('RFC', 'Rfc'), ('FAW', 'Faw'), ('SUP', 'Sup'), ('MGD', 'Mgd'), ('SAW', 'Saw'), ('SUP_RFC', 'Sup Rfc'), ('RFC_PCO', 'Rfc Pco'), ('RFC_RFC', 'Rfc Rfc')], default=None, max_length=255)),
                ('assessment_version', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='saris_assessment.assessmentversion')),
            ],
            options={
                'verbose_name': 'Assessment Rule',
                'verbose_name_plural': 'assessment rule',
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='AwardScheme',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.BigAutoField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('program_type', models.CharField(choices=[('UNDERGRADUATE', 'Undergraduate'), ('POSTGRADUATE', 'Postgraduate')], max_length=255)),
                ('min_cgpa', models.FloatField()),
                ('max_cgpa', models.FloatField()),
                ('repeated', models.BooleanField(default=False)),
                ('award_class', models.CharField(max_length=255)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('assessment_version', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='saris_assessment.assessmentversion')),
            ],
            options={
                'verbose_name': 'Award Scheme',
                'verbose_name_plural': 'award scheme',
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='GradeBook',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('PROCESSING', 'Processing'), ('READY', 'Ready'), ('ERROR', 'Error')], default='PENDING', max_length=45)),
                ('error', models.CharField(blank=True, max_length=255, null=True)),
                ('pdf_file', models.FileField(blank=True, null=True, upload_to='saris_assessment/gradebook')),
                ('academic_semester', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='saris_calendar.academicsemester')),
                ('faculty', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='saris_institution.faculty')),
            ],
            options={
                'verbose_name': 'Grade Book',
                'verbose_name_plural': 'grade books',
            },
            bases=(saris.models.WorkMixin, dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='GradeScheme',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.BigAutoField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('min_grade', models.FloatField()),
                ('max_grade', models.FloatField()),
                ('letter_grade', models.CharField(max_length=255)),
                ('grade_point', models.FloatField()),
                ('grade_quality', models.CharField(max_length=255)),
                ('decision', models.CharField(max_length=255)),
                ('grade_scheme_version', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='saris_assessment.gradeschemeversion')),
            ],
            options={
                'verbose_name': 'Grade Scheme',
                'verbose_name_plural': 'grade scheme',
                'ordering': ['-min_grade'],
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='LecturerCourse',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='saris_curriculum.course')),
                ('lecturer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='account.staff')),
            ],
            options={
                'verbose_name': 'Lecturer Course',
                'verbose_name_plural': 'lecturer courses',
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='PublishedGrade',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('course_type', models.CharField(choices=[('CORE', 'Core'), ('NONCORE', 'Noncore'), ('ELECTIVE', 'Elective'), ('AUDIT', 'Audit')], max_length=255)),
                ('course_attempt', models.CharField(choices=[('NORMAL', 'Normal'), ('CARRYOVER', 'Carryover'), ('REPEAT', 'Repeat'), ('SUP', 'Sup')], max_length=255)),
                ('semester', models.IntegerField()),
                ('continous_grade', models.FloatField(blank=True, null=True)),
                ('endsemester_grade', models.FloatField(blank=True, null=True)),
                ('final_grade', models.FloatField(blank=True, null=True)),
                ('grade_point', models.FloatField(blank=True, null=True)),
                ('letter_grade', models.CharField(blank=True, max_length=5, null=True)),
                ('academic_semester', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='saris_calendar.academicsemester')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='saris_curriculum.course')),
                ('enrollment', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='saris_admission.enrollment')),
            ],
            options={
                'verbose_name': 'Published Grades',
                'verbose_name_plural': 'published grades',
                'ordering': ['course__code'],
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='PublishedResult',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('semester', models.IntegerField()),
                ('semester_gpa', models.FloatField(blank=True, null=True)),
                ('semester_credits', models.FloatField(blank=True, null=True)),
                ('cumulative_gpa', models.FloatField(blank=True, null=True)),
                ('cumulative_credits', models.FloatField(blank=True, null=True)),
                ('decision', models.CharField(choices=[('PAP', 'Pap'), ('PCO', 'Pco'), ('RFC', 'Rfc'), ('FAW', 'Faw'), ('SUP', 'Sup'), ('MGD', 'Mgd'), ('SAW', 'Saw'), ('SUP_RFC', 'Sup Rfc'), ('RFC_PCO', 'Rfc Pco'), ('RFC_RFC', 'Rfc Rfc')], default=None, max_length=255)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('academic_semester', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='saris_calendar.academicsemester')),
                ('enrollment', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='saris_admission.enrollment')),
            ],
            options={
                'verbose_name': 'Published Results',
                'verbose_name_plural': 'published results',
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SemesterResult',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('semester', models.IntegerField()),
                ('semester_gpa', models.FloatField(blank=True, null=True)),
                ('semester_credits', models.FloatField(blank=True, null=True)),
                ('cumulative_gpa', models.FloatField(blank=True, null=True)),
                ('cumulative_credits', models.FloatField(blank=True, null=True)),
                ('decision', models.CharField(choices=[('PAP', 'Pap'), ('PCO', 'Pco'), ('RFC', 'Rfc'), ('FAW', 'Faw'), ('SUP', 'Sup'), ('MGD', 'Mgd'), ('SAW', 'Saw'), ('SUP_RFC', 'Sup Rfc'), ('RFC_PCO', 'Rfc Pco'), ('RFC_RFC', 'Rfc Rfc')], default=None, max_length=255)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('academic_semester', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='saris_calendar.academicsemester')),
                ('enrollment', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='saris_admission.enrollment')),
            ],
            options={
                'verbose_name': 'Semester Result',
                'verbose_name_plural': 'semester results',
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='StudentCourse',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('course_type', models.CharField(choices=[('CORE', 'Core'), ('NONCORE', 'Noncore'), ('ELECTIVE', 'Elective'), ('AUDIT', 'Audit')], max_length=255)),
                ('course_attempt', models.CharField(choices=[('NORMAL', 'Normal'), ('CARRYOVER', 'Carryover'), ('REPEAT', 'Repeat'), ('SUP', 'Sup')], max_length=255)),
                ('semester', models.IntegerField()),
                ('continous_grade', models.FloatField(blank=True, null=True)),
                ('endsemester_grade', models.FloatField(blank=True, null=True)),
                ('final_grade', models.FloatField(blank=True, null=True)),
                ('grade_point', models.FloatField(blank=True, null=True)),
                ('letter_grade', models.CharField(blank=True, max_length=5, null=True)),
                ('academic_semester', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='saris_calendar.academicsemester')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='saris_curriculum.course')),
                ('enrollment', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='saris_admission.enrollment')),
            ],
            options={
                'verbose_name': 'Student Course',
                'verbose_name_plural': 'student courses',
                'ordering': ['course__code'],
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='CourseAppeal',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('appeal_type', models.CharField(choices=[('MISSING GRADE', 'Missing Grade'), ('GRADE CORRECTION', 'Grade Correction'), ('COURSE REMARK', 'Course Remark')], max_length=255)),
                ('old_continous_grade', models.FloatField(blank=True, null=True)),
                ('old_endsemester_grade', models.FloatField(blank=True, null=True)),
                ('new_continous_grade', models.FloatField(blank=True, null=True)),
                ('new_endsemester_grade', models.FloatField(blank=True, null=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('RESOLVED', 'Resolved')], default='PENDING', max_length=255)),
                ('student_course', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='saris_assessment.studentcourse')),
            ],
            options={
                'verbose_name': 'Course Appeal',
                'verbose_name_plural': 'course appeals',
                'ordering': ['-student_course__semester'],
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
    ]
