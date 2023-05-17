import secrets
import string


letters = string.ascii_letters
digits = string.digits
special_chars = string.punctuation

alphabet = letters + digits + special_chars


def get_password(pwd_length: int = 10, meeting_limit: int = 2) -> str:
    while True:
        pwd = ''
        for i in range(pwd_length):
            pwd += ''.join(secrets.choice(alphabet))

        if (any(char in special_chars for char in pwd) and 
            sum(char in digits for char in pwd) >= meeting_limit):
                break
        
    return pwd
