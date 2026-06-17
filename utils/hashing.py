import bcrypt

salt = bcrypt.gensalt()

def hash_pswd(pswd: str) -> str:
    pswd_bytes = pswd.encode('utf-8')
    hashed_bytes = bcrypt.hashpw(pswd_bytes, salt)
    return hashed_bytes.decode('utf-8')

def check_pswd(hashed: str, original: str) -> bool:
    return bcrypt.checkpw(original.encode('utf-8'), hashed.encode('utf-8'))