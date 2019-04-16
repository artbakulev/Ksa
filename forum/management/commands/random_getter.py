import random

from django.db.models import Max


def get_random(Obj, number=1):
    max_id = Obj.objects.all().aggregate(max_id=Max("id"))['max_id']
    if number == 1:
        while True:
            pk = random.randint(1, max_id)
            obj = Obj.objects.filter(pk=pk).first()
            if obj:
                return obj
    else:
        total = 0
        objects = []
        while total < number:
            pk = random.randint(1, max_id)
            obj = Obj.objects.filter(pk=pk).first()
            if obj:
                total += 1
                objects.append(obj)
        return objects
