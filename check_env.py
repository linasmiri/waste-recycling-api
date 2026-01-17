
try:
    import bcrypt
    print("bcrypt imported successfully")
except ImportError as e:
    print(f"bcrypt import failed: {e}")

try:
    from jose import jwt
    print("python-jose imported successfully")
except ImportError as e:
    print(f"python-jose import failed: {e}")

try:
    from fastapi import FastAPI
    print("fastapi imported successfully")
except ImportError as e:
    print(f"fastapi import failed: {e}")
