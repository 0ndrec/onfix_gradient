
import random
import string

def generate_password(length: int=12) -> str:
    if length < 8:
        raise ValueError('Password length should be at least 8 characters')
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    symbols = '!@#$%^&*'
    password = [random.choice(lowercase), random.choice(uppercase), random.choice(digits), random.choice(symbols)]
    for _ in range(length - 4):
        password.append(random.choice(lowercase + uppercase + digits + symbols))
    random.shuffle(password)
    return ''.join(password)