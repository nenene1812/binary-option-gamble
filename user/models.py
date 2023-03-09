from django.db import models

# Create your models here.
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)

from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
import uuid
from .utils import generate_ref_code

class UserManager(BaseUserManager):
    """ Class user """
    def create_user(self, email, password = None):
        """Function create nomal users"""
        if email is None:
            raise TypeError('User should have a Email')

        user = self.model(email = self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user 

    def create_superuser(self, email, password = None):
        """Function create nomal users"""
        if password is None:
            raise TypeError('password should not be none')
        
        user = self.create_user(email,password)
        user.is_superuser = True
        user.is_staff = True 
        user.save()
        return user

class User(AbstractBaseUser,PermissionsMixin):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False,unique=True,db_index=True)
    username = models.CharField(max_length=255 )
    email = models.EmailField(max_length=255, unique=True,db_index=True )
    recommand_by = models.CharField(max_length=255 )
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
 
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return str(self.id)

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return str(refresh.access_token)
    