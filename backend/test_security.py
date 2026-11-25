
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

# 1. Password hashing
password = "ResearchifyTest@123"

hashed = hash_password(password)

assert hashed != password
print("Password hashing: SUCCESS")

# 2. Password verification
assert verify_password(password, hashed)
assert not verify_password("WrongPassword", hashed)

print("Password verification: SUCCESS")

# 3. JWT creation
user_id = "11111111-1111-4111-8111-111111111111"

token = create_access_token(user_id)

print("JWT generation: SUCCESS")

# 4. JWT decoding
payload = decode_access_token(token)

assert payload["sub"] == user_id

print("JWT validation: SUCCESS")

print("\nAll security tests passed!")
