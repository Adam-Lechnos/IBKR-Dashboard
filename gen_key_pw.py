from cryptography.fernet import Fernet

key = Fernet.generate_key()
f = Fernet(key)
password = f.encrypt(b'inputPW')
print(f'IBEAM_PASSWORD={password}, IBEAM_KEY={key}')