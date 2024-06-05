from cryptography.fernet import Fernet

key = Fernet.generate_key()
f = Fernet(key)
password = f.encrypt(b'HhT2LR4CawJkEVDgWb5qUS8YMy7pfvZdN9cGQzKs')
print(f'IBEAM_PASSWORD={password}, IBEAM_KEY={key}')