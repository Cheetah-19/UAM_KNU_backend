from django.db import models


class Vertiport(models.Model):
    name = models.CharField(primary_key=True, default='', max_length=20, null=False, blank=False, unique=True)
    fato = models.SmallIntegerField(default=0, null=False, blank=False)
    path_in = models.SmallIntegerField(default=0, null=False, blank=False)
    gate = models.SmallIntegerField(default=0, null=False, blank=False)
    path_out = models.SmallIntegerField(default=0, null=False, blank=False)
    waiting_room = models.SmallIntegerField(default=0, null=False, blank=False)

    # DB 테이블 이름
    class Meta:
        db_table = 'vertiport'

    def __str__(self):
        return self.name
