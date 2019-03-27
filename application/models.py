from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionManager, PermissionsMixin, BaseUserManager, Permission
from datetime import datetime
from django.utils.timezone import now
# Create your models here.
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin


class DemoUserManager(BaseUserManager):

    # def get_query_set(self):
    #     import pdb; pdb.set_trace()
    #     return super(DemoUserManager, self).get_query_set()

    # def create_user(self, username, email, password):
    def create_user(self, username, password):
        if not username:
            raise ValueError('user must have an username')
        if not password:
            raise ValueError('user must have an password')
        # if not email:
        #     raise ValueError('email must have an email')
        user = self.model(username=username)
        # user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.view_password = password
        user.create_time = now()
        user.update_time = now()
        user.expire_day = 30
        user.is_superuser = False
        user.save(using=self._db)
        return user

    # def create_superuser(self, username, email, password):
    def create_superuser(self, username, password):
        user = self.create_user(username, password)
        user.is_admin = True
        user.expire_day = None
        user.is_superuser = True
        user.save(using=self._db)
        return user

class DemoUser(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    username = models.CharField(max_length=127,unique=True)
    # email = models.CharField(max_length=255, unique=True, verbose_name='email_address')
    password = models.CharField(max_length=255)
    view_password = models.CharField(max_length=15, default="")
    create_time = models.DateField(auto_now_add=True, blank=True)
    update_time = models.DateField(auto_now_add=True, blank=True)
    expire_day = models.IntegerField(default=30, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    objects = DemoUserManager()

    class Meta:
        db_table = 'user'
        default_permissions = ()
        permissions = (
            ('view_hello', 'Can view hello word'),
        )


    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def get_short_name(self):
        return self.username

    def get_username(self):
        return self.username

    @property
    def is_expired(self):
        return False

    @property
    def is_staff(self):
        return self.is_admin

    # def has_perm(self, perm, obj=None):
    #     # import pdb; pdb.set_trace()
    #     return super().has_perm(perm, obj)

    # def has_perms(self, perm_list, obj=None):
    #     return super().has_perms(perm_list, obj)


    # def has_module_perms(self, app_label):
    #     return super().has_module_perms(app_label)


class UploadFileMetaData(models.Model):
    old_name = models.CharField(max_length=255)
    md5 = models.CharField(max_length=255, unique=True)
    out_type = models.CharField(max_length=16, default='upload')
    upload_time = models.DateField(auto_now_add=True, verbose_name='文件创建日期')
    ext = models.CharField(max_length=16, verbose_name='文件类型')
    user_id = models.IntegerField(verbose_name='上传文件的user_id')

    class Meta:
        default_permissions = ()

class OutputFileMetaData(models.Model):
    filename = models.CharField(max_length=255)
    md5 = models.CharField(max_length=255, unique=True)
    out_type = models.CharField(max_length=16, default='output')
    create_time = models.DateField(auto_now_add=True, verbose_name='文件创建日期')
    ext = models.CharField(max_length=16, verbose_name='文件类型')

    class Meta:
        default_permissions = ()

class File(models.Model):
    md5 = models.CharField(max_length=25, unique=True, default="")
    binary = models.BinaryField(max_length=(2**32-1))

    class Meta:
        default_permissions = ()