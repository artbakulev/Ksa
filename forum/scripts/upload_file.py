import os

from Ksa.settings import MEDIA_ROOT


def handle_uploaded_file(f, filename, extra_path=''):
    path = os.path.join(MEDIA_ROOT, extra_path)
    if not os.path.exists(path):
        os.makedirs(path)
    with open(os.path.join(path, filename), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
