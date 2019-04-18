import hashlib

def hash_md5(pwd):
    hashes = hashlib.md5(b'dsjhdsahduksan')
    hashes.update(pwd.encode('utf-8'))
    return hashes.hexdigest()