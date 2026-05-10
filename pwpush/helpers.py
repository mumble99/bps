from base64 import b64decode, b64encode
from string import ascii_lowercase, digits
from random import choices
from hashlib import sha256


def random_string(lenght=10):
    return ''.join(choices(ascii_lowercase + digits, k=lenght))

def hash_password(password):
    return sha256(password.encode()).hexdigest()

def to_string_if_value_present(value):
    result = None

    if value:
        result = value.decode()

    return result

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

class Secret:
    def __init__(self, key=None):
        self.key = key
        self.first_time_init = True if not self.key else False
        if self.first_time_init:
            self.key = random_string()
        self.key_type = f"{self.key}_type"
        self.key_view_count = f"{self.key}_view_count"
        self.key_filename = f"{self.key}_filename"
        self.key_password = f"{self.key}_password"
    
    def set_secret(self, rds, secret_json, max_data_lenght):
        status = False

        secret_type = secret_json.get("type")
        secret_expire = secret_json.get("expire")
        secret_view_count = secret_json.get("view_count")
        secret_filename = secret_json.get("filename")
        secret_password = secret_json.get("password")
        secret_data = secret_json.get("data")

        if validate_secret_type(secret_type) and validate_integer(secret_expire) and validate_integer(secret_view_count) and secret_data:
            try:
                secret_data = b64decode(secret_data)
            except:
                pass
            else:
                if len(secret_data) <= max_data_lenght:
                    rds.setex(self.key, secret_expire, secret_data)
                    rds.setex(self.key_type, secret_expire, secret_type)
                    rds.setex(self.key_view_count, secret_expire, secret_view_count)
                    if secret_filename:
                        rds.setex(self.key_filename, secret_expire, secret_filename)
                    if secret_password:
                        rds.setex(self.key_password, secret_expire, hash_password(secret_password))
                    
                    status = True
        
        return status

    def get_secret(self, rds):
        result = {}

        view_count = rds.get(self.key_view_count)
        if view_count:
            try:
                view_count = int(view_count.decode())
            except:
                pass
            else:
                rds.decr(self.key_view_count)
                result["key_type"] = to_string_if_value_present(rds.get(self.key_type))
                result["view_count"] = view_count
                result["filename"] = to_string_if_value_present(rds.get(self.key_filename))
                result["password"] = to_string_if_value_present(rds.get(self.key_password))
                data = rds.get(self.key)
                if data:
                    data = b64encode(data).decode()
                result["data"] = data

                if view_count <= 1:
                    self.delete_secret(rds)

        return result

    def delete_secret(self, rds):
        rds.delete(self.key_type)
        rds.delete(self.key_view_count)
        rds.delete(self.key_filename)
        rds.delete(self.key_password)
        rds.delete(self.key)
    
    def secret_exists(self, rds):
        exists = False
        secret_password = None

        if rds.get(self.key_view_count):
            exists = True
            secret_password = to_string_if_value_present(rds.get(self.key_password))
        
        return exists, secret_password
        