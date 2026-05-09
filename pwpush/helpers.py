from string import ascii_lowercase, digits
from random import choices
from time import time


def random_string(lenght=10):
    return ''.join(choices(ascii_lowercase + digits, k=lenght))


def validate_integer(integer):
    status = False

    if isinstance(integer, int) and integer > 0:
        status = True
    
    return status

def validate_secret_type(secret_type):
    status = False

    if secret_type in ["file", "data"]:
        status = True

    return status

def get_and_validate_view_count(view_count):
    status = False
    validated_view_count = None

    if view_count:
        view_count = int(view_count.decode())
        if view_count > 0:
            status = True
        validated_view_count = view_count
    
    return status, validated_view_count