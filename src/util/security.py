from cryptography.fernet import Fernet
import bcrypt
import os

# THESE KEYS ARE VISIBLE KEYS AND ARE NOT INTENDED FOR PRODUCTION
# SEPARATE KEYS MUST BE DECLARED FOR PRODUCTION
# THESE KEYS ARE ONLY INTENDED FOR DEVELOPMENT
f1 = Fernet(os.getenv("FERNET_KEY_1", "XF6OymR9AUpgZE9j_O3H7oY_9EwrEvCs7O2sYQmyskk=").encode())
f2 = Fernet(os.getenv("FERNET_KEY_2", "HovvX4QOJd-cpGKGPmqqY3EH0AGbw1gfHmQM2LpIrRo=").encode())
f3 = Fernet(os.getenv("FERNET_KEY_3", "WziTQwFIoHbqAU8KvY7Lc5wIRfE6LfjdaW3Lm7pnc0U=").encode())


def enc(s: str) -> str:
    return f1.encrypt(s.encode()).decode()


def dec(s: str) -> str:
    return f1.decrypt(s.encode()).decode()


def enc2(s: str) -> str:
    return f2.encrypt(s.encode()).decode()


def dec2(s: str) -> str:
    return f2.decrypt(s.encode()).decode()


def enc_pwd(pwd: str) -> str:
    return f3.encrypt(bcrypt.hashpw(pwd.encode(), bcrypt.gensalt())).decode()


def check_pwd(pwd: str, hash_: str) -> bool:
    return bcrypt.checkpw(pwd.encode(), f3.decrypt(hash_.encode()))
