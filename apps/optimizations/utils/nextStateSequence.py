from ..models import State
from django.db.models import Max


def nextStateSequence(user, vertiport):
    max_sequence = State.objects.filter(user=user, vertiport=vertiport).aggregate(Max('sequence'))['sequence__max']

    if max_sequence is None:
        return 1
    else:
        return max_sequence + 1
