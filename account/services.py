from django.contrib.auth.models import Group
from saris_institution.models import Campus
from .models import User


class Signatory(object):
    VICE_CHANCELLOR = 'Vice Chancellor'
    UNIVERSITY_REGISTRAR = 'University Registrar'
    COLLEGE_REGISTRAR = 'College Registrar'

    @staticmethod
    def get_by_role(name: str):
        try:
            group = Group.objects.get(name=name)
            user = group.user_set.first()
            user.group = group
            return user
        except Group.DoesNotExist:
            raise Group.DoesNotExist
        except User.DoesNotExist:
            raise User.DoesNotExist
        
    @staticmethod    
    def get_by_campus(role: str, campus: Campus):
        try:
            group = Group.objects.get(name=role)
            user = group.user_set.filter(campus=campus).first()
            user.group = group
            return user
        except Group.DoesNotExist:
            raise Group.DoesNotExist
        except User.DoesNotExist:
            raise User.DoesNotExist

    @staticmethod    
    def vice_chancellor():
        return Signatory.get_by_role(Signatory.VICE_CHANCELLOR)
    
    @staticmethod    
    def university_registrar():
        return Signatory.get_by_role(Signatory.UNIVERSITY_REGISTRAR)
    
    @staticmethod    
    def college_registrar(campus):
        if not isinstance(campus, Campus):
            campus = Campus.objects.get(pk=campus)
        return Signatory.get_by_campus(Signatory.COLLEGE_REGISTRAR, campus)
    
    
class UserAccount(object):
    
    def __init__(self, first_name, last_name, email) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def create_student(self):
        user = User() 
        user.first_name = self.first_name
        user.last_name = self.last_name
        user.set_email(self.email)
        user.set_username(self.email)
        user.set_default_password()
        user.set_active()
        user.set_student()
        user.save()
        return user  

    def create_staff(self):
        user = User() 
        user.first_name = self.first_name
        user.last_name = self.last_name
        user.set_email(self.email)
        user.set_username(self.email)
        user.set_default_password()
        user.set_active()
        user.set_staff()
        user.save()
        return user   