from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    # 일반 user 생성
    def create_user(self, id, password, phone_number):
        if not id:
            raise ValueError('must have an user id')
        user = self.model(
            id=id,
            phone_number=phone_number
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    # 관리자 user 생성
    def create_superuser(self, id, password, phone_number):
        user = self.create_user(
            id=id,
            password=password,
            phone_number=phone_number
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    id = models.CharField(primary_key=True, default='', max_length=100, null=False, blank=False, unique=True)
    phone_number = models.CharField(default='', max_length=11, null=False, blank=False, unique=True)

    # User 모델의 필수 필드와 메서드
    is_admin = models.BooleanField(default=False)

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    # Helper 클래스
    objects = UserManager()

    # User의 username 필드는 id로 설정
    USERNAME_FIELD = 'id'

    # 필수로 작성해야하는 필드
    REQUIRED_FIELDS = ['password', 'phone_number']

    # DB 테이블 이름
    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.id
